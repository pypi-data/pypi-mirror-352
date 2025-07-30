"""
Coverage Gap Detector

Identifies implementations with zero test coverage using the Knowledge Graph.
"""

from typing import Dict, List, Optional, Any, Iterator
import os
import json
import logging
from datetime import datetime

from testindex_knowledge_contract.schema import (
    IMPL_LABEL, GAP_LABEL, PROP_ID, PROP_PATH, PROP_START, PROP_END, PROP_COVER
)
# Use our simplified client to avoid dependency issues
from testindex.analysis.coverage.utils import SimpleNeo4jClient
from testindex.analysis.coverage.models import CoverageGap

# Define relationship type that's not in the schema contract
REL_HAS_GAP = "HAS_GAP"

# Setup logging
logger = logging.getLogger(__name__)


class GapDetector:
    """Detects implementations with zero or low test coverage."""
    
    def __init__(self, 
                 neo4j_client: Optional[SimpleNeo4jClient] = None,
                 coverage_threshold: float = 0.0,
                 batch_size: int = 100):
        """Initialize the gap detector.
        
        Args:
            neo4j_client: Neo4j client for Knowledge Graph access
            coverage_threshold: Coverage percentage threshold (0-100)
                                Default 0.0 means only detect zero coverage
            batch_size: Size of batches for processing large datasets
        """
        self.neo4j_client = neo4j_client or SimpleNeo4jClient()
        self.coverage_threshold = coverage_threshold
        self.batch_size = batch_size
        self.run_timestamp = datetime.now().isoformat()
    
    def find_gaps(self) -> List[Dict[str, Any]]:
        """Find implementations with coverage below threshold.
        
        Returns:
            List of dictionaries containing implementation data for gaps
        """
        query = f"""
        MATCH (impl:{IMPL_LABEL})
        WHERE impl.{PROP_COVER} <= $threshold
        RETURN 
            impl.{PROP_ID} as id,
            impl.{PROP_PATH} as path,
            impl.{PROP_START} as line_start,
            impl.{PROP_END} as line_end,
            impl.{PROP_COVER} as coverage
        """
        
        results = self.neo4j_client.run_query(query, {'threshold': self.coverage_threshold})
        return results
    
    def find_gaps_batched(self) -> Iterator[List[Dict[str, Any]]]:
        """Find implementations with coverage below threshold in batches.
        
        Yields:
            Batches of dictionaries containing implementation data for gaps
        """
        query = f"""
        MATCH (impl:{IMPL_LABEL})
        WHERE impl.{PROP_COVER} <= $threshold
        RETURN 
            impl.{PROP_ID} as id,
            impl.{PROP_PATH} as path,
            impl.{PROP_START} as line_start,
            impl.{PROP_END} as line_end,
            impl.{PROP_COVER} as coverage
        SKIP $skip LIMIT $limit
        """
        
        skip = 0
        while True:
            parameters = {
                'threshold': self.coverage_threshold,
                'skip': skip,
                'limit': self.batch_size
            }
            
            batch = self.neo4j_client.run_query(query, parameters)
            
            if not batch:
                break
                
            yield batch
            
            if len(batch) < self.batch_size:
                break
                
            skip += self.batch_size
    
    def export_gaps_json(self, output_file: str) -> str:
        """Export gap data to JSON file.
        
        Args:
            output_file: Path to the output JSON file
            
        Returns:
            Path to the created file
        """
        gaps = self.find_gaps()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Create CoverageGap objects
        gap_objects = [CoverageGap.from_implementation(gap) for gap in gaps]
        
        # Write to JSON file
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': self.run_timestamp,
                'total_gaps': len(gap_objects),
                'coverage_threshold': self.coverage_threshold,
                'gaps': [gap.to_dict() for gap in gap_objects]
            }, f, indent=2)
            
        return output_file
    
    def store_gaps_in_neo4j(self) -> int:
        """Store identified gaps back into Neo4j.
        
        Creates CoverageGap nodes and HAS_GAP relationships between
        Implementation and CoverageGap nodes.
        
        Returns:
            Number of gaps stored
        """
        processed_count = 0
        
        # Process in batches for large repositories
        for batch in self.find_gaps_batched():
            batch_results = self._store_gap_batch(batch)
            processed_count += batch_results
            logger.info(f"Processed batch of {len(batch)} gaps, total: {processed_count}")
            
        return processed_count
    
    def _store_gap_batch(self, gaps: List[Dict[str, Any]]) -> int:
        """Store a batch of gaps in Neo4j.
        
        Args:
            gaps: List of gap dictionaries to store
            
        Returns:
            Number of gaps stored
        """
        # Prepare Cypher query
        query = f"""
        MATCH (i:{IMPL_LABEL}) WHERE i.{PROP_ID} = $impl_id
        MERGE (g:{GAP_LABEL} {{
            {PROP_ID}: i.{PROP_ID},
            path: i.{PROP_PATH},
            line_start: i.{PROP_START},
            line_end: i.{PROP_END},
            coverage: i.{PROP_COVER},
            detected_at: $detected_at,
            version: $version
        }})
        MERGE (i)-[:{REL_HAS_GAP}]->(g)
        RETURN g.{PROP_ID} as gap_id
        """
        
        # Process each gap
        processed_count = 0
        for gap in gaps:
            try:
                # Create CoverageGap object with timestamp
                gap_obj = CoverageGap.from_implementation(gap)
                gap_obj.detected_at = self.run_timestamp
                
                # Store in Neo4j
                result = self.neo4j_client.run_query(query, {
                    'impl_id': gap_obj.implementation_id,
                    'detected_at': gap_obj.detected_at,
                    'version': gap_obj.version
                })
                
                if result:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing gap {gap['id']}: {str(e)}")
                
        return processed_count
    
    def find_changed_gaps(self, previous_run_timestamp: str) -> Dict[str, List]:
        """Find new and resolved gaps between runs.
        
        Args:
            previous_run_timestamp: Timestamp of previous run to compare against
            
        Returns:
            Dictionary with 'new_gaps' and 'resolved_gaps' lists
        """
        # Find previous gaps
        previous_query = f"""
        MATCH (g:{GAP_LABEL})
        WHERE g.detected_at <= $previous_timestamp
        RETURN g.{PROP_ID} as id
        """
        
        # Find current gaps
        current_query = f"""
        MATCH (g:{GAP_LABEL})
        WHERE g.detected_at = $current_timestamp
        RETURN g.{PROP_ID} as id
        """
        
        try:
            # Get previous and current gap IDs
            previous_gaps = [
                record['id'] for record in 
                self.neo4j_client.run_query(previous_query, {'previous_timestamp': previous_run_timestamp})
            ]
            
            current_gaps = [
                record['id'] for record in 
                self.neo4j_client.run_query(current_query, {'current_timestamp': self.run_timestamp})
            ]
            
            # Calculate differences
            new_gaps = [id for id in current_gaps if id not in previous_gaps]
            resolved_gaps = [id for id in previous_gaps if id not in current_gaps]
            
            return {
                'new_gaps': new_gaps,
                'resolved_gaps': resolved_gaps
            }
        except Exception as e:
            logger.error(f"Error detecting gap changes: {str(e)}")
            return {'new_gaps': [], 'resolved_gaps': []}
    
    def get_gap_details(self, gap_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for specific gaps.
        
        Args:
            gap_ids: List of gap IDs to retrieve
            
        Returns:
            List of dictionaries with gap details
        """
        if not gap_ids:
            return []
            
        query = f"""
        MATCH (g:{GAP_LABEL})
        WHERE g.{PROP_ID} IN $gap_ids
        RETURN g.{PROP_ID} as id,
               g.path as path,
               g.line_start as line_start,
               g.line_end as line_end,
               g.coverage as coverage,
               g.detected_at as detected_at,
               g.version as version
        """
        
        return self.neo4j_client.run_query(query, {'gap_ids': gap_ids})


if __name__ == "__main__":
    # Simple CLI usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect code coverage gaps")
    parser.add_argument("--output", "-o", default="gaps.json", 
                        help="Output JSON file path")
    parser.add_argument("--threshold", "-t", type=float, default=0.0,
                        help="Coverage threshold (0-100)")
    parser.add_argument("--store", "-s", action="store_true",
                        help="Store gaps in Neo4j")
    parser.add_argument("--batch-size", "-b", type=int, default=100,
                       help="Batch size for processing large repositories")
    parser.add_argument("--previous-run", "-p", type=str,
                       help="Previous run timestamp for change detection")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize detector
    detector = GapDetector(
        coverage_threshold=args.threshold,
        batch_size=args.batch_size
    )
    
    # Find gaps
    gaps = detector.find_gaps()
    logger.info(f"Found {len(gaps)} coverage gaps")
    
    # Export to JSON
    output_file = detector.export_gaps_json(args.output)
    logger.info(f"Exported gaps to {output_file}")
    
    # Store in Neo4j if requested
    if args.store:
        stored_count = detector.store_gaps_in_neo4j()
        logger.info(f"Stored {stored_count} gaps in Neo4j")
        
    # Compare with previous run if specified
    if args.previous_run:
        changes = detector.find_changed_gaps(args.previous_run)
        logger.info(f"New gaps: {len(changes['new_gaps'])}")
        logger.info(f"Resolved gaps: {len(changes['resolved_gaps'])}")
        
        if changes['new_gaps']:
            new_gap_details = detector.get_gap_details(changes['new_gaps'])
            logger.info(f"New gap details: {new_gap_details}") 