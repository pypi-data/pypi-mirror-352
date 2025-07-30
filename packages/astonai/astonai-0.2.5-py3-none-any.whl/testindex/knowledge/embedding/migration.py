#!/usr/bin/env python3
"""
Migration utilities for vector stores.

This module provides utilities for migrating vectors between different
vector store implementations, with support for validation, progress tracking,
and resumable operations.
"""

import os
import time
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field

from tqdm.asyncio import tqdm
import numpy as np

from testindex.knowledge.embedding.vector_store import VectorStoreInterface
from testindex.knowledge.errors import BatchOperationError, VectorOperationError

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    
    # Number of vectors processed
    total_vectors: int = 0
    
    # Number of vectors successfully migrated
    migrated_vectors: int = 0
    
    # Number of vectors that failed to migrate
    failed_vectors: int = 0
    
    # Duration of the migration in seconds
    duration_seconds: float = 0.0
    
    # IDs of vectors that were successfully migrated
    migrated_ids: List[str] = field(default_factory=list)
    
    # IDs of vectors that failed to migrate with error messages
    failed_ids: Dict[str, str] = field(default_factory=dict)
    
    # Checksum of all migrated vectors for validation
    source_checksum: str = ""
    target_checksum: str = ""
    
    # Start and end times
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_vectors": self.total_vectors,
            "migrated_vectors": self.migrated_vectors,
            "failed_vectors": self.failed_vectors,
            "duration_seconds": self.duration_seconds,
            "migrated_ids": self.migrated_ids,
            "failed_ids": self.failed_ids,
            "source_checksum": self.source_checksum,
            "target_checksum": self.target_checksum,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save migration result to a file.
        
        Args:
            file_path: Path to save the result to
        """
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'MigrationResult':
        """Load migration result from a file.
        
        Args:
            file_path: Path to load the result from
            
        Returns:
            MigrationResult object
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Convert datetime strings back to datetime objects
        if data.get("start_time"):
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        
        return cls(**data)
    
    @property
    def success_rate(self) -> float:
        """Get the success rate of the migration.
        
        Returns:
            Success rate as a percentage
        """
        if self.total_vectors == 0:
            return 0.0
        return (self.migrated_vectors / self.total_vectors) * 100.0
    
    @property
    def checksum_match(self) -> bool:
        """Check if source and target checksums match.
        
        Returns:
            True if checksums match, False otherwise
        """
        if not self.source_checksum or not self.target_checksum:
            return False
        return self.source_checksum == self.target_checksum


def calculate_checksum(vectors: List[Tuple[str, np.ndarray]]) -> str:
    """Calculate a checksum for a collection of vectors.
    
    This is used to verify that all vectors were migrated correctly.
    
    Args:
        vectors: List of (id, vector) tuples
        
    Returns:
        Checksum string
    """
    if not vectors:
        return ""
    
    # Sort vectors by ID to ensure consistent order
    vectors = sorted(vectors, key=lambda x: x[0])
    
    # Concatenate all vector data
    all_values = []
    for _, vector in vectors:
        # Round to reduce floating point precision differences
        rounded = np.round(vector, decimals=6)
        all_values.extend(rounded.tolist())
    
    # Hash the concatenated values
    import hashlib
    checksum = hashlib.sha256(str(all_values).encode()).hexdigest()
    return checksum


async def get_all_vectors(
    store: VectorStoreInterface,
    filter_metadata: Optional[Dict[str, Any]] = None,
    batch_size: int = 100,
    show_progress: bool = True
) -> List[Tuple[str, np.ndarray, Dict]]:
    """Get all vectors from a vector store.
    
    Args:
        store: Vector store to get vectors from
        filter_metadata: Optional filter criteria
        batch_size: Number of vectors to retrieve in each batch
        show_progress: Whether to show a progress bar
        
    Returns:
        List of (id, vector, metadata) tuples
    """
    # First, get the total count for progress tracking
    total_count = await store.count_vectors(filter_metadata)
    
    if total_count == 0:
        logger.info("No vectors found matching filter criteria")
        return []
    
    # We don't have a direct way to get all vectors with pagination in the interface,
    # so we'll implement a workaround using search with a dummy vector

    # Create a dummy query that will match everything
    # This assumes the store's search will return vectors even with a low similarity
    dummy_vector = np.zeros(1536, dtype=np.float32)  # Adjust dimension if needed
    
    # We need to search in batches to avoid loading everything at once
    all_vectors = []
    seen_ids = set()
    
    # Setup progress bar
    pbar = None
    if show_progress:
        pbar = tqdm(total=total_count, desc="Retrieving vectors")
    
    # Loop until we've retrieved all vectors
    page = 0
    while len(all_vectors) < total_count:
        try:
            # Search for a batch of vectors
            results = await store.search_vectors(
                query_vector=dummy_vector,
                limit=batch_size,
                score_threshold=0.0,  # Include all vectors
                filter_metadata=filter_metadata
            )
            
            # If no results, we're done
            if not results:
                break
            
            # Process each result
            for result in results:
                vector_id = result.id
                
                # Skip if we've already seen this vector
                if vector_id in seen_ids:
                    continue
                
                # Get the full vector
                vector, metadata = await store.get_vector(vector_id)
                
                if vector is not None and metadata is not None:
                    all_vectors.append((vector_id, vector, metadata))
                    seen_ids.add(vector_id)
            
            # Update progress bar
            if pbar:
                pbar.update(len(results))
            
            # Increment page
            page += 1
            
        except Exception as e:
            logger.error(f"Error retrieving batch {page}: {str(e)}")
            # Continue to next batch
            page += 1
    
    # Close progress bar
    if pbar:
        pbar.close()
    
    return all_vectors


async def migrate_vectors(
    source_store: VectorStoreInterface,
    target_store: VectorStoreInterface,
    batch_size: int = 100,
    filter_metadata: Optional[Dict[str, Any]] = None,
    resume_from: Optional[MigrationResult] = None,
    show_progress: bool = True,
    validate: bool = True
) -> MigrationResult:
    """Migrate vectors from one store to another.
    
    Args:
        source_store: Source vector store
        target_store: Target vector store
        batch_size: Number of vectors to migrate in each batch
        filter_metadata: Optional filter criteria for vectors to migrate
        resume_from: Optional previous migration result to resume from
        show_progress: Whether to show a progress bar
        validate: Whether to validate the migration by comparing checksums
        
    Returns:
        MigrationResult object with migration statistics
    """
    # Initialize result
    result = MigrationResult()
    result.start_time = datetime.now()
    
    # If resuming, initialize from previous result
    already_migrated_ids = set()
    if resume_from:
        logger.info(f"Resuming migration with {len(resume_from.migrated_ids)} already migrated vectors")
        already_migrated_ids = set(resume_from.migrated_ids)
        result.migrated_ids = resume_from.migrated_ids.copy()
        result.failed_ids = resume_from.failed_ids.copy()
        result.migrated_vectors = len(resume_from.migrated_ids)
        result.failed_vectors = len(resume_from.failed_ids)
    
    try:
        # Get all vectors from source store
        logger.info("Retrieving vectors from source store...")
        source_vectors = await get_all_vectors(
            source_store,
            filter_metadata=filter_metadata,
            batch_size=batch_size,
            show_progress=show_progress
        )
        
        # Update total count
        result.total_vectors = len(source_vectors)
        
        if result.total_vectors == 0:
            logger.info("No vectors to migrate")
            return result
        
        # Calculate source checksum if validation is enabled
        if validate:
            logger.info("Calculating source checksum...")
            source_vectors_for_checksum = [(vid, vec) for vid, vec, _ in source_vectors]
            result.source_checksum = calculate_checksum(source_vectors_for_checksum)
        
        # Filter out already migrated vectors if resuming
        if resume_from:
            source_vectors = [v for v in source_vectors if v[0] not in already_migrated_ids]
            logger.info(f"After filtering already migrated vectors, {len(source_vectors)} remain")
        
        # Migrate vectors in batches
        logger.info(f"Migrating {len(source_vectors)} vectors in batches of {batch_size}...")
        
        # Process in batches
        batches = [source_vectors[i:i+batch_size] for i in range(0, len(source_vectors), batch_size)]
        
        # Setup progress bar
        pbar = None
        if show_progress:
            pbar = tqdm(total=len(source_vectors), desc="Migrating vectors")
        
        # Process each batch
        for batch_idx, batch in enumerate(batches):
            try:
                # Prepare batch for migration
                vectors = []
                metadatas = []
                vector_ids = []
                
                for vector_id, vector, metadata in batch:
                    vectors.append(vector)
                    metadatas.append(metadata)
                    vector_ids.append(vector_id)
                
                # Store vectors in target store
                migrated_ids = await target_store.batch_store_vectors(
                    vectors=vectors,
                    metadata_list=metadatas,
                    vector_ids=vector_ids
                )
                
                # Update result
                result.migrated_ids.extend(migrated_ids)
                result.migrated_vectors += len(migrated_ids)
                
                # Update progress bar
                if pbar:
                    pbar.update(len(batch))
                
                logger.debug(f"Migrated batch {batch_idx+1}/{len(batches)} with {len(batch)} vectors")
                
            except Exception as e:
                logger.error(f"Error migrating batch {batch_idx+1}: {str(e)}")
                
                # Record failed vectors
                for vector_id, _, _ in batch:
                    result.failed_ids[vector_id] = str(e)
                    result.failed_vectors += 1
                
                # Update progress bar
                if pbar:
                    pbar.update(len(batch))
        
        # Close progress bar
        if pbar:
            pbar.close()
        
        # Validate migration if requested
        if validate:
            logger.info("Validating migration...")
            
            # Get all vectors from target store
            target_vectors = await get_all_vectors(
                target_store,
                filter_metadata=filter_metadata,
                batch_size=batch_size,
                show_progress=show_progress
            )
            
            # Calculate target checksum
            target_vectors_for_checksum = [(vid, vec) for vid, vec, _ in target_vectors]
            result.target_checksum = calculate_checksum(target_vectors_for_checksum)
            
            # Check if checksums match
            if result.checksum_match:
                logger.info("Migration validated successfully")
            else:
                logger.warning("Migration validation failed: checksums do not match")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        # Record the error in the result
        result.failed_ids["migration_error"] = str(e)
    
    # Update duration and end time
    result.end_time = datetime.now()
    result.duration_seconds = (result.end_time - result.start_time).total_seconds()
    
    # Log summary
    logger.info(f"Migration completed: {result.migrated_vectors}/{result.total_vectors} vectors migrated "
                f"({result.success_rate:.2f}%) in {result.duration_seconds:.2f}s")
    
    if result.failed_vectors > 0:
        logger.warning(f"{result.failed_vectors} vectors failed to migrate")
    
    return result


async def clean_target_store(
    source_store: VectorStoreInterface,
    target_store: VectorStoreInterface,
    migration_result: MigrationResult
) -> None:
    """Clean up the target store after migration.
    
    This removes any vectors from the target store that don't exist in the source store.
    
    Args:
        source_store: Source vector store
        target_store: Target vector store
        migration_result: Result of the migration operation
    """
    logger.info("Cleaning target store...")
    
    # Get all vector IDs from source store
    source_vectors = await get_all_vectors(source_store, show_progress=False)
    source_ids = {v[0] for v in source_vectors}
    
    # Get all vector IDs from target store
    target_vectors = await get_all_vectors(target_store, show_progress=False)
    target_ids = {v[0] for v in target_vectors}
    
    # Find IDs that exist in target but not in source
    to_delete = target_ids - source_ids
    
    if not to_delete:
        logger.info("No vectors to clean up")
        return
    
    logger.info(f"Deleting {len(to_delete)} vectors from target store...")
    
    # Delete in batches
    batch_size = 100
    to_delete_list = list(to_delete)
    batches = [to_delete_list[i:i+batch_size] for i in range(0, len(to_delete_list), batch_size)]
    
    # Setup progress bar
    with tqdm(total=len(to_delete), desc="Cleaning vectors") as pbar:
        for batch in batches:
            for vector_id in batch:
                try:
                    await target_store.delete_vector(vector_id)
                except Exception as e:
                    logger.warning(f"Failed to delete vector {vector_id}: {str(e)}")
                pbar.update(1)
    
    logger.info(f"Cleaned up {len(to_delete)} vectors from target store")


async def verify_migration(
    source_store: VectorStoreInterface,
    target_store: VectorStoreInterface,
    filter_metadata: Optional[Dict[str, Any]] = None,
    sample_size: int = 100
) -> Tuple[bool, Dict[str, Any]]:
    """Verify that a migration was successful by comparing vector similarity.
    
    Args:
        source_store: Source vector store
        target_store: Target vector store
        filter_metadata: Optional filter criteria
        sample_size: Number of vectors to sample for verification
        
    Returns:
        Tuple of (success, details) where success is a boolean indicating if the
        verification passed, and details is a dictionary with verification metrics
    """
    logger.info(f"Verifying migration with a sample of {sample_size} vectors...")
    
    # Get all vector IDs from source store
    source_vectors = await get_all_vectors(source_store, filter_metadata=filter_metadata, show_progress=False)
    source_ids = {v[0] for v in source_vectors}
    
    # Get all vector IDs from target store
    target_vectors = await get_all_vectors(target_store, filter_metadata=filter_metadata, show_progress=False)
    target_ids = {v[0] for v in target_vectors}
    
    # Check if all source vectors exist in target
    missing_in_target = source_ids - target_ids
    if missing_in_target:
        logger.warning(f"{len(missing_in_target)} vectors missing in target store")
        return False, {
            "success": False,
            "missing_in_target": list(missing_in_target)[:100],  # Limit to 100 IDs
            "missing_count": len(missing_in_target)
        }
    
    # Check if there are any extra vectors in target
    extra_in_target = target_ids - source_ids
    if extra_in_target:
        logger.warning(f"{len(extra_in_target)} extra vectors in target store")
    
    # Sample random vectors for detailed verification
    import random
    sample_ids = random.sample(list(source_ids), min(sample_size, len(source_ids)))
    
    # Verify each sampled vector
    different_vectors = []
    cosine_similarities = []
    different_metadata = []
    
    for vector_id in tqdm(sample_ids, desc="Verifying vectors"):
        # Get vector from source
        source_vector, source_metadata = await source_store.get_vector(vector_id)
        
        # Get vector from target
        target_vector, target_metadata = await target_store.get_vector(vector_id)
        
        # Check if vectors match
        if source_vector is None or target_vector is None:
            logger.warning(f"Vector {vector_id} missing in one of the stores")
            different_vectors.append(vector_id)
            continue
        
        # Calculate cosine similarity
        source_norm = np.linalg.norm(source_vector)
        target_norm = np.linalg.norm(target_vector)
        
        if source_norm > 0 and target_norm > 0:
            cosine_similarity = np.dot(source_vector, target_vector) / (source_norm * target_norm)
            cosine_similarities.append(cosine_similarity)
            
            # Consider vectors different if similarity < 0.999
            if cosine_similarity < 0.999:
                different_vectors.append(vector_id)
        
        # Check if metadata matches
        # Focus on core fields only
        source_core = {
            "source_type": source_metadata.source_type,
            "source_id": source_metadata.source_id,
            "content_type": source_metadata.content_type,
            "content": source_metadata.content
        }
        target_core = {
            "source_type": target_metadata.source_type,
            "source_id": target_metadata.source_id,
            "content_type": target_metadata.content_type,
            "content": target_metadata.content
        }
        
        if source_core != target_core:
            different_metadata.append(vector_id)
    
    # Calculate verification metrics
    avg_similarity = sum(cosine_similarities) / len(cosine_similarities) if cosine_similarities else 0.0
    success = len(different_vectors) == 0 and len(different_metadata) == 0
    
    details = {
        "success": success,
        "vectors_sampled": len(sample_ids),
        "different_vectors": different_vectors,
        "different_metadata": different_metadata,
        "average_similarity": avg_similarity,
        "extra_in_target": list(extra_in_target)[:100] if extra_in_target else [],
        "extra_count": len(extra_in_target)
    }
    
    if success:
        logger.info("Migration verification passed")
    else:
        logger.warning("Migration verification failed")
        logger.warning(f"  Different vectors: {len(different_vectors)}")
        logger.warning(f"  Different metadata: {len(different_metadata)}")
        logger.warning(f"  Average similarity: {avg_similarity:.4f}")
    
    return success, details


async def estimate_migration_time(
    source_store: VectorStoreInterface,
    target_store: VectorStoreInterface,
    filter_metadata: Optional[Dict[str, Any]] = None,
    sample_size: int = 10
) -> Dict[str, Any]:
    """Estimate the time required for migration.
    
    Args:
        source_store: Source vector store
        target_store: Target vector store
        filter_metadata: Optional filter criteria
        sample_size: Number of vectors to sample for estimation
        
    Returns:
        Dictionary with estimation metrics
    """
    logger.info(f"Estimating migration time with a sample of {sample_size} vectors...")
    
    # Count total vectors
    total_count = await source_store.count_vectors(filter_metadata)
    
    if total_count == 0:
        logger.info("No vectors to migrate")
        return {
            "total_vectors": 0,
            "estimated_time_seconds": 0,
            "estimated_time_minutes": 0,
            "estimated_time_hours": 0
        }
    
    # Sample random vectors
    source_vectors = await get_all_vectors(
        source_store,
        filter_metadata=filter_metadata,
        batch_size=sample_size,
        show_progress=False
    )
    
    if len(source_vectors) == 0:
        logger.warning("Failed to retrieve sample vectors")
        return {
            "total_vectors": total_count,
            "estimated_time_seconds": None,
            "estimated_time_minutes": None,
            "estimated_time_hours": None
        }
    
    # Limit to sample size
    sample_vectors = source_vectors[:sample_size]
    
    # Time the migration of sample vectors
    start_time = time.time()
    
    # Prepare batch for migration
    vectors = []
    metadatas = []
    vector_ids = []
    
    for vector_id, vector, metadata in sample_vectors:
        vectors.append(vector)
        metadatas.append(metadata)
        vector_ids.append(f"test_{vector_id}")  # Use different IDs to avoid conflicts
    
    # Store vectors in target store
    try:
        await target_store.batch_store_vectors(
            vectors=vectors,
            metadata_list=metadatas,
            vector_ids=vector_ids
        )
        
        # Clean up test vectors
        for vector_id in vector_ids:
            await target_store.delete_vector(vector_id)
    except Exception as e:
        logger.warning(f"Error during estimation: {str(e)}")
        return {
            "total_vectors": total_count,
            "estimated_time_seconds": None,
            "estimated_time_minutes": None,
            "estimated_time_hours": None,
            "error": str(e)
        }
    
    # Calculate time per vector
    end_time = time.time()
    elapsed_seconds = end_time - start_time
    time_per_vector = elapsed_seconds / len(sample_vectors)
    
    # Estimate total time
    estimated_time_seconds = time_per_vector * total_count
    estimated_time_minutes = estimated_time_seconds / 60
    estimated_time_hours = estimated_time_minutes / 60
    
    logger.info(f"Estimated migration time: {estimated_time_hours:.2f} hours "
                f"({estimated_time_minutes:.2f} minutes)")
    
    return {
        "total_vectors": total_count,
        "sample_size": len(sample_vectors),
        "time_per_vector_seconds": time_per_vector,
        "estimated_time_seconds": estimated_time_seconds,
        "estimated_time_minutes": estimated_time_minutes,
        "estimated_time_hours": estimated_time_hours
    } 