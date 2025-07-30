"""
Adapter for converting code chunks to Knowledge Graph nodes.

This module provides an adapter for converting CodeChunk objects from
the preprocessing pod to appropriate Knowledge Graph nodes and building
relationships between them based on chunk dependencies.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Generator
from pathlib import Path

from testindex.core.logging import get_logger
from testindex.core.exceptions import AstonError
from testindex.preprocessing.chunking.code_chunker import CodeChunk, ChunkType

# Import knowledge graph types for type hints only
# These are used for documentation, we don't modify or instantiate them directly
from testindex.knowledge.schema.base import Node, Relationship

logger = get_logger(__name__)


class ChunkGraphAdapterError(AstonError):
    """Custom exception for errors during chunk graph adaptation."""
    error_code = "ADAPTER001"
    default_message = "An error occurred during chunk graph adaptation."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, operation: Optional[str] = None):
        final_message = message or self.default_message
        if operation:
            final_message = f"{final_message} Operation: {operation}"

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=context
        )
        self.operation = operation


class ChunkGraphAdapter:
    """Adapter for converting code chunks to knowledge graph nodes."""
    
    def __init__(self, neo4j_client=None):
        """Initialize with optional Neo4j client.
        
        Args:
            neo4j_client: Optional Neo4j client instance for direct graph operations
        """
        self.neo4j_client = neo4j_client
        self.logger = get_logger("chunk-graph-adapter")
    
    def chunk_to_node(self, chunk: CodeChunk) -> Dict[str, Any]:
        """Convert a single code chunk to a knowledge graph node dictionary.
        
        Args:
            chunk: CodeChunk object to convert
            
        Returns:
            Dict[str, Any]: Dictionary representation of a node
            
        Raises:
            ChunkGraphAdapterError: If chunk conversion fails
        """
        try:
            # Map chunk type to appropriate node type
            if chunk.chunk_type == ChunkType.MODULE:
                return self._chunk_to_module_node(chunk)
            elif chunk.chunk_type in (ChunkType.FUNCTION, ChunkType.METHOD, ChunkType.NESTED_FUNCTION):
                return self._chunk_to_implementation_node(chunk)
            elif chunk.chunk_type in (ChunkType.CLASS, ChunkType.NESTED_CLASS):
                return self._chunk_to_implementation_node(chunk)
            elif chunk.chunk_type == ChunkType.STANDALONE_CODE:
                return self._chunk_to_implementation_node(chunk)
            else:
                raise ChunkGraphAdapterError(f"Unsupported chunk type: {chunk.chunk_type}")
        
        except Exception as e:
            error_msg = f"Failed to convert chunk to node: {str(e)}"
            self.logger.error(error_msg, extra={"chunk_id": chunk.chunk_id})
            raise ChunkGraphAdapterError(error_msg, details={
                "chunk_id": chunk.chunk_id,
                "chunk_type": chunk.chunk_type.value,
                "error": str(e)
            })
    
    def _chunk_to_module_node(self, chunk: CodeChunk) -> Dict[str, Any]:
        """Convert a module chunk to a module node dictionary.
        
        Args:
            chunk: Module chunk to convert
            
        Returns:
            Dict[str, Any]: Dictionary representation of a ModuleNode
        """
        # Create a unique ID for the node based on the chunk ID
        node_id = f"module_{chunk.chunk_id}"
        
        # Create node dictionary
        return {
            "type": "Module",
            "id": node_id,
            "name": chunk.name,
            "file_path": str(chunk.source_file),
            "description": chunk.doc_string,
            "properties": {
                "chunk_id": chunk.chunk_id,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "imports": chunk.imports,
                "is_package": chunk.metadata.get("is_package", False)
            }
        }
    
    def _chunk_to_implementation_node(self, chunk: CodeChunk) -> Dict[str, Any]:
        """Convert a function, method, or class chunk to an implementation node dictionary.
        
        Args:
            chunk: Function, method, or class chunk to convert
            
        Returns:
            Dict[str, Any]: Dictionary representation of an ImplementationNode
        """
        # Create a unique ID for the node based on the chunk ID
        node_id = f"impl_{chunk.chunk_id}"
        
        # Create base node dictionary
        node_dict = {
            "type": "Implementation",
            "id": node_id,
            "name": chunk.name,
            "file_path": str(chunk.source_file),
            "line_number": chunk.start_line,
            "description": chunk.doc_string,
            "properties": {
                "chunk_id": chunk.chunk_id,
                "chunk_type": chunk.chunk_type.value,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "decorators": chunk.decorators
            }
        }
        
        # Add type-specific properties
        if chunk.chunk_type in (ChunkType.FUNCTION, ChunkType.METHOD, ChunkType.NESTED_FUNCTION):
            node_dict["properties"]["is_async"] = chunk.is_async
            node_dict["properties"]["function_args"] = chunk.metadata.get("args", {})
            node_dict["properties"]["return_type"] = chunk.metadata.get("returns")
            
        elif chunk.chunk_type in (ChunkType.CLASS, ChunkType.NESTED_CLASS):
            node_dict["properties"]["base_classes"] = chunk.metadata.get("base_classes", [])
            
        return node_dict
    
    def build_relationship(self, source_node_id: str, target_node_id: str, 
                          rel_type: str, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a relationship dictionary between two nodes.
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            rel_type: Relationship type
            properties: Optional relationship properties
            
        Returns:
            Dict[str, Any]: Dictionary representation of a relationship
        """
        # Create a unique ID for the relationship
        rel_id = f"{source_node_id}_{rel_type}_{target_node_id}"
        
        # Create relationship dictionary
        return {
            "id": rel_id,
            "type": rel_type,
            "source_id": source_node_id,
            "target_id": target_node_id,
            "properties": properties or {}
        }
    
    def process_chunks(self, chunks: List[CodeChunk], batch_size: int = 100) -> Dict[str, str]:
        """Process multiple chunks and return mapping of chunk_ids to node_ids.
        
        Args:
            chunks: List of code chunks to process
            batch_size: Number of chunks to process in a batch
            
        Returns:
            Dict[str, str]: Mapping of chunk_ids to node_ids
            
        Raises:
            ChunkGraphAdapterError: If chunk processing fails
        """
        chunk_node_map = {}
        
        # Process chunks in batches
        for batch in self._batch_chunks(chunks, batch_size):
            try:
                batch_map = {}
                for chunk in batch:
                    # Convert chunk to node dictionary
                    node_dict = self.chunk_to_node(chunk)
                    
                    # Validate that node_dict contains required keys
                    if "id" not in node_dict:
                        raise ChunkGraphAdapterError(
                            f"Missing 'id' in node dictionary for chunk {chunk.chunk_id}",
                            details={"chunk_id": chunk.chunk_id, "node_dict": str(node_dict)}
                        )
                    
                    # Map chunk ID to node ID
                    batch_map[chunk.chunk_id] = node_dict["id"]
                    
                    # If Neo4j client is provided, create the node
                    if self.neo4j_client:
                        try:
                            if node_dict["type"] == "Module":
                                # We need to import the actual ModuleNode class here
                                # to create the node using the Neo4j client
                                from testindex.knowledge.schema.nodes import ModuleNode
                                
                                # Make sure all required fields have values
                                name = node_dict.get("name", "unknown")
                                file_path = node_dict.get("file_path", "unknown")
                                description = node_dict.get("description", "")
                                node_id = node_dict["id"]
                                properties = node_dict.get("properties", {})
                                
                                self.logger.debug(f"Creating ModuleNode: {name}, id={node_id}")
                                
                                node = ModuleNode(
                                    name=name,
                                    file_path=file_path,
                                    description=description,
                                    id=node_id,
                                    properties=properties
                                )
                                self.neo4j_client.create_node(node)
                            else:
                                # We need to import the actual ImplementationNode class here
                                # to create the node using the Neo4j client
                                from testindex.knowledge.schema.nodes import ImplementationNode
                                
                                # Make sure all required fields have values
                                name = node_dict.get("name", "unknown")
                                file_path = node_dict.get("file_path", "unknown")
                                line_number = node_dict.get("line_number", 0)
                                description = node_dict.get("description", "")
                                node_id = node_dict["id"]
                                properties = node_dict.get("properties", {})
                                
                                self.logger.debug(f"Creating ImplementationNode: {name}, id={node_id}")
                                
                                node = ImplementationNode(
                                    name=name,
                                    file_path=file_path,
                                    line_number=line_number,
                                    description=description,
                                    id=node_id,
                                    properties=properties
                                )
                                self.neo4j_client.create_node(node)
                        except Exception as node_error:
                            self.logger.error(f"Failed to create node for chunk {chunk.chunk_id}: {str(node_error)}")
                            self.logger.error(f"Node dict: {node_dict}")
                            raise ChunkGraphAdapterError(
                                f"Failed to create node for chunk {chunk.chunk_id}",
                                details={"chunk_id": chunk.chunk_id, "error": str(node_error)}
                            )
                
                # Update the overall mapping
                chunk_node_map.update(batch_map)
                
                self.logger.info(f"Processed batch of {len(batch)} chunks")
                
            except Exception as e:
                error_msg = f"Failed to process chunk batch: {str(e)}"
                self.logger.error(error_msg)
                raise ChunkGraphAdapterError(error_msg, details={"error": str(e)})
        
        return chunk_node_map
    
    def build_relationships(self, chunks: List[CodeChunk], chunk_node_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Build relationships between nodes based on chunk dependencies.
        
        Args:
            chunks: List of code chunks
            chunk_node_map: Mapping of chunk_ids to node_ids
            
        Returns:
            List[Dict[str, Any]]: List of relationship dictionaries
            
        Raises:
            ChunkGraphAdapterError: If relationship building fails
        """
        relationships = []
        error_details = {
            "parent_child_errors": [],
            "dependency_errors": [],
            "import_errors": []
        }
        
        try:
            # Build parent-child relationships
            for chunk in chunks:
                try:
                    # Skip chunks without a parent
                    if not chunk.parent_chunk_id:
                        continue
                    
                    # Get node IDs from the map
                    if chunk.chunk_id in chunk_node_map and chunk.parent_chunk_id in chunk_node_map:
                        child_node_id = chunk_node_map[chunk.chunk_id]
                        parent_node_id = chunk_node_map[chunk.parent_chunk_id]
                        
                        # Create CONTAINS relationship
                        rel = self.build_relationship(
                            source_node_id=parent_node_id,
                            target_node_id=child_node_id,
                            rel_type="CONTAINS",
                            properties={"relation_type": "parent_child"}
                        )
                        relationships.append(rel)
                        
                        # If Neo4j client is provided, create the relationship
                        if self.neo4j_client:
                            try:
                                from testindex.knowledge.schema.relationships import ContainsRelationship
                                rel_obj = ContainsRelationship(
                                    source_id=parent_node_id,
                                    target_id=child_node_id,
                                    id=rel["id"],
                                    properties=rel["properties"]
                                )
                                self.neo4j_client.create_relationship(rel_obj)
                            except Exception as rel_error:
                                error_msg = f"Failed to create CONTAINS relationship: {str(rel_error)}"
                                self.logger.error(error_msg, extra={
                                    "chunk_id": chunk.chunk_id,
                                    "parent_id": chunk.parent_chunk_id,
                                    "error": str(rel_error)
                                })
                                error_details["parent_child_errors"].append({
                                    "chunk_id": chunk.chunk_id,
                                    "parent_id": chunk.parent_chunk_id,
                                    "error": str(rel_error)
                                })
                except Exception as chunk_error:
                    error_msg = f"Error processing parent-child relationship for chunk {chunk.chunk_id}: {str(chunk_error)}"
                    self.logger.error(error_msg)
                    error_details["parent_child_errors"].append({
                        "chunk_id": chunk.chunk_id,
                        "error": str(chunk_error)
                    })
            
            # Build dependency relationships
            for chunk in chunks:
                try:
                    # Skip chunks without dependencies
                    if not chunk.dependencies:
                        continue
                    
                    # Get node ID for this chunk
                    if chunk.chunk_id not in chunk_node_map:
                        continue
                    
                    source_node_id = chunk_node_map[chunk.chunk_id]
                    
                    # Create a map of dependency names to corresponding chunks
                    dependency_map = {}
                    for c in chunks:
                        dependency_map[c.name] = c
                    
                    # Process each dependency
                    for dep_name in chunk.dependencies:
                        try:
                            # Find the chunk that matches this dependency name
                            if dep_name in dependency_map:
                                dep_chunk = dependency_map[dep_name]
                                
                                # Skip if the dependency chunk is not in the node map
                                if dep_chunk.chunk_id not in chunk_node_map:
                                    continue
                                
                                target_node_id = chunk_node_map[dep_chunk.chunk_id]
                                
                                # Create CALLS or INHERITS_FROM relationship based on chunk types
                                if chunk.chunk_type in (ChunkType.FUNCTION, ChunkType.METHOD, ChunkType.NESTED_FUNCTION):
                                    rel_type = "CALLS"
                                elif chunk.chunk_type in (ChunkType.CLASS, ChunkType.NESTED_CLASS):
                                    rel_type = "INHERITS_FROM"
                                else:
                                    rel_type = "DEPENDS_ON"
                                
                                rel = self.build_relationship(
                                    source_node_id=source_node_id,
                                    target_node_id=target_node_id,
                                    rel_type=rel_type,
                                    properties={"dependency_name": dep_name}
                                )
                                relationships.append(rel)
                                
                                # If Neo4j client is provided, create the relationship
                                if self.neo4j_client:
                                    try:
                                        if rel_type == "CALLS":
                                            from testindex.knowledge.schema.relationships import CallsRelationship
                                            rel_obj = CallsRelationship(
                                                source_id=source_node_id,
                                                target_id=target_node_id,
                                                id=rel["id"],
                                                properties=rel["properties"]
                                            )
                                        elif rel_type == "INHERITS_FROM":
                                            from testindex.knowledge.schema.relationships import InheritsFromRelationship
                                            rel_obj = InheritsFromRelationship(
                                                source_id=source_node_id,
                                                target_id=target_node_id,
                                                id=rel["id"],
                                                properties=rel["properties"]
                                            )
                                        else:
                                            # Generic fallback
                                            from testindex.knowledge.schema.base import Relationship
                                            rel_obj = Relationship(
                                                type=rel_type,
                                                source_id=source_node_id,
                                                target_id=target_node_id,
                                                id=rel["id"],
                                                properties=rel["properties"]
                                            )
                                        self.neo4j_client.create_relationship(rel_obj)
                                    except Exception as rel_error:
                                        error_msg = f"Failed to create {rel_type} relationship: {str(rel_error)}"
                                        self.logger.error(error_msg, extra={
                                            "chunk_id": chunk.chunk_id,
                                            "dependency": dep_name,
                                            "error": str(rel_error)
                                        })
                                        error_details["dependency_errors"].append({
                                            "chunk_id": chunk.chunk_id,
                                            "dependency": dep_name,
                                            "rel_type": rel_type,
                                            "error": str(rel_error)
                                        })
                        except Exception as dep_error:
                            error_msg = f"Error processing dependency {dep_name} for chunk {chunk.chunk_id}: {str(dep_error)}"
                            self.logger.error(error_msg)
                            error_details["dependency_errors"].append({
                                "chunk_id": chunk.chunk_id,
                                "dependency": dep_name,
                                "error": str(dep_error)
                            })
                except Exception as chunk_error:
                    error_msg = f"Error processing dependencies for chunk {chunk.chunk_id}: {str(chunk_error)}"
                    self.logger.error(error_msg)
                    error_details["dependency_errors"].append({
                        "chunk_id": chunk.chunk_id,
                        "error": str(chunk_error)
                    })
            
            # Build import relationships for modules
            for chunk in chunks:
                try:
                    # Skip non-module chunks
                    if chunk.chunk_type != ChunkType.MODULE:
                        continue
                    
                    # Skip chunks without imports
                    if not chunk.imports:
                        continue
                    
                    # Get node ID for this chunk
                    if chunk.chunk_id not in chunk_node_map:
                        continue
                    
                    source_node_id = chunk_node_map[chunk.chunk_id]
                    
                    # Maps module names to node IDs
                    module_map = {}
                    for c in chunks:
                        if c.chunk_type == ChunkType.MODULE:
                            module_name = c.name
                            # Also map with full path for absolute imports
                            full_path = str(c.source_file)
                            if c.chunk_id in chunk_node_map:
                                module_map[module_name] = chunk_node_map[c.chunk_id]
                                module_map[full_path] = chunk_node_map[c.chunk_id]
                    
                    # Process each import
                    for import_stmt in chunk.imports:
                        try:
                            # Extract module name from import statement
                            # This is a simplified approach, actual implementation may need more parsing
                            module_name = import_stmt.split()[1].split('.')[0]
                            
                            if module_name in module_map:
                                target_node_id = module_map[module_name]
                                
                                rel = self.build_relationship(
                                    source_node_id=source_node_id,
                                    target_node_id=target_node_id,
                                    rel_type="IMPORTS",
                                    properties={"import_statement": import_stmt}
                                )
                                relationships.append(rel)
                                
                                # If Neo4j client is provided, create the relationship
                                if self.neo4j_client:
                                    try:
                                        from testindex.knowledge.schema.relationships import ImportsRelationship
                                        rel_obj = ImportsRelationship(
                                            source_id=source_node_id,
                                            target_id=target_node_id,
                                            id=rel["id"],
                                            properties=rel["properties"]
                                        )
                                        self.neo4j_client.create_relationship(rel_obj)
                                    except Exception as rel_error:
                                        error_msg = f"Failed to create IMPORTS relationship: {str(rel_error)}"
                                        self.logger.error(error_msg, extra={
                                            "chunk_id": chunk.chunk_id,
                                            "import": import_stmt,
                                            "error": str(rel_error)
                                        })
                                        error_details["import_errors"].append({
                                            "chunk_id": chunk.chunk_id,
                                            "import": import_stmt,
                                            "error": str(rel_error)
                                        })
                        except Exception as import_error:
                            error_msg = f"Error processing import {import_stmt} for chunk {chunk.chunk_id}: {str(import_error)}"
                            self.logger.error(error_msg)
                            error_details["import_errors"].append({
                                "chunk_id": chunk.chunk_id,
                                "import": import_stmt,
                                "error": str(import_error)
                            })
                except Exception as chunk_error:
                    error_msg = f"Error processing imports for chunk {chunk.chunk_id}: {str(chunk_error)}"
                    self.logger.error(error_msg)
                    error_details["import_errors"].append({
                        "chunk_id": chunk.chunk_id,
                        "error": str(chunk_error)
                    })
        
        except Exception as e:
            error_msg = f"Failed to build relationships: {str(e)}"
            self.logger.error(error_msg)
            raise ChunkGraphAdapterError(error_msg, details={
                "error": str(e),
                "error_details": error_details
            })
        
        # Log summary of relationship creation
        total_errors = (
            len(error_details["parent_child_errors"]) +
            len(error_details["dependency_errors"]) +
            len(error_details["import_errors"])
        )
        
        if total_errors > 0:
            self.logger.warning(
                f"Relationship creation completed with {total_errors} errors: "
                f"{len(error_details['parent_child_errors'])} parent-child, "
                f"{len(error_details['dependency_errors'])} dependency, "
                f"{len(error_details['import_errors'])} import errors"
            )
        else:
            self.logger.info(f"Successfully created {len(relationships)} relationships")
        
        return relationships
    
    def _batch_chunks(self, chunks: List[CodeChunk], batch_size: int) -> Generator[List[CodeChunk], None, None]:
        """Split chunks into batches for efficient processing.
        
        Args:
            chunks: List of chunks to batch
            batch_size: Size of each batch
            
        Yields:
            List[CodeChunk]: Batch of chunks
        """
        for i in range(0, len(chunks), batch_size):
            yield chunks[i:i + batch_size] 