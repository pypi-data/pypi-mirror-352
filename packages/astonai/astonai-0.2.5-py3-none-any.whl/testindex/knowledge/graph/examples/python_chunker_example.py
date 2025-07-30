#!/usr/bin/env python3
"""
Example script demonstrating how to use the Python Code Chunker to analyze Python
code and build a knowledge graph based on the code structure analysis.
"""

import os
import logging
import tempfile
from pathlib import Path
from collections import Counter
from typing import Dict, List

from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker, ChunkType, CodeChunk
from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter
from testindex.knowledge.graph.neo4j_client import Neo4jClient

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_code(temp_dir: Path) -> Dict[str, Path]:
    """Create sample Python files for testing the code chunker.
    
    Args:
        temp_dir: Directory where the sample files will be created
        
    Returns:
        Dictionary mapping file names to their Path objects
    """
    # Define sample code files
    files = {
        "models.py": """
from dataclasses import dataclass
from typing import List, Optional
import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime.datetime
    is_active: bool = True
    
    def get_display_name(self) -> str:
        return f"{self.username} ({self.email})"
    
    def deactivate(self) -> None:
        self.is_active = False
        
@dataclass
class Post:
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime.datetime
    tags: Optional[List[str]] = None
    
    def get_summary(self, max_length: int = 100) -> str:
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
""",

        "repository.py": """
from typing import Dict, List, Optional
from .models import User, Post

class Repository:
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._posts: Dict[int, Post] = {}
    
    def add_user(self, user: User) -> None:
        self._users[user.id] = user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def add_post(self, post: Post) -> None:
        self._posts[post.id] = post
    
    def get_posts_by_author(self, author_id: int) -> List[Post]:
        return [post for post in self._posts.values() if post.author_id == author_id]

class UserRepository(Repository):
    def get_active_users(self) -> List[User]:
        return [user for user in self._users.values() if user.is_active]
    
    def search_by_username(self, username_prefix: str) -> List[User]:
        return [
            user for user in self._users.values() 
            if user.username.startswith(username_prefix)
        ]
""",

        "service.py": """
from typing import List, Optional
from datetime import datetime
from .models import User, Post
from .repository import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def create_user(self, username: str, email: str) -> User:
        # In a real app, this would generate a unique ID
        user_id = len(self.repository._users) + 1
        user = User(
            id=user_id,
            username=username,
            email=email,
            created_at=datetime.now()
        )
        self.repository.add_user(user)
        return user
    
    def create_post(self, author_id: int, title: str, content: str, tags: Optional[List[str]] = None) -> Post:
        # Verify the user exists
        user = self.repository.get_user(author_id)
        if not user:
            raise ValueError(f"User with ID {author_id} not found")
            
        # In a real app, this would generate a unique ID
        post_id = len(self.repository._posts) + 1
        post = Post(
            id=post_id,
            title=title,
            content=content,
            author_id=author_id,
            created_at=datetime.now(),
            tags=tags
        )
        self.repository.add_post(post)
        return post

def main():
    # Set up repositories and services
    repository = UserRepository()
    user_service = UserService(repository)
    
    # Create some users
    alice = user_service.create_user("alice", "alice@example.com")
    bob = user_service.create_user("bob", "bob@example.com")
    
    # Create some posts
    user_service.create_post(
        alice.id, 
        "Hello World", 
        "This is my first post!",
        ["introduction", "hello"]
    )
    user_service.create_post(
        alice.id, 
        "Python Tips", 
        "Python is a great language for productivity.",
        ["python", "programming"]
    )
    user_service.create_post(
        bob.id, 
        "My Thoughts", 
        "Just sharing some random thoughts...",
        ["personal"]
    )
    
    # Get posts by author
    alice_posts = repository.get_posts_by_author(alice.id)
    print(f"Alice has {len(alice_posts)} posts")
    
    # Search users
    a_users = repository.search_by_username("a")
    print(f"Found {len(a_users)} users starting with 'a'")

if __name__ == "__main__":
    main()
"""
    }
    
    # Create the files in the temporary directory
    file_paths = {}
    for filename, content in files.items():
        file_path = temp_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        file_paths[filename] = file_path
    
    return file_paths

def analyze_single_file(chunker: PythonCodeChunker, file_path: Path) -> List[CodeChunk]:
    """Analyze a single Python file and display the chunks.
    
    Args:
        chunker: The PythonCodeChunker instance
        file_path: Path to the Python file to analyze
        
    Returns:
        List of CodeChunks extracted from the file
    """
    logger.info(f"Analyzing file: {file_path}")
    chunks = chunker.chunk_file(file_path)
    
    # Summarize the chunks
    chunk_types = Counter([chunk.chunk_type.value for chunk in chunks])
    logger.info(f"Found {len(chunks)} chunks: {dict(chunk_types)}")
    
    # Display details for each chunk
    for chunk in chunks:
        logger.info(f"{chunk.chunk_type.value}: {chunk.name} "
                    f"(Lines {chunk.start_line}-{chunk.end_line})")
        
        if chunk.parent_chunk_id:
            parent = next((c for c in chunks if c.chunk_id == chunk.parent_chunk_id), None)
            if parent:
                logger.info(f"  Parent: {parent.chunk_type.value}: {parent.name}")
        
        if chunk.dependencies:
            logger.info(f"  Dependencies: {', '.join(chunk.dependencies)}")
        
        if chunk.imports:
            logger.info(f"  Imports: {', '.join(chunk.imports)}")
    
    return chunks

def build_knowledge_graph(chunker: PythonCodeChunker, 
                          adapter: ChunkGraphAdapter, 
                          directory: Path) -> None:
    """Build a knowledge graph from the code chunks in the directory.
    
    Args:
        chunker: The PythonCodeChunker instance
        adapter: The ChunkGraphAdapter instance
        directory: Directory containing Python files to analyze
    """
    logger.info(f"Processing directory: {directory}")
    
    # Process all Python files in the directory
    chunks = chunker.chunk_directory(directory)
    logger.info(f"Found {len(chunks)} chunks across all files")
    
    # Add chunks to the knowledge graph
    chunk_node_map = adapter.process_chunks(chunks)
    logger.info(f"Created {len(chunk_node_map)} nodes in the knowledge graph")
    
    # Build relationships between nodes
    relationships = adapter.build_relationships(chunks, chunk_node_map)
    logger.info(f"Created {len(relationships)} relationships in the knowledge graph")
    
    # Display some example queries that can be run
    logger.info("Example Neo4j queries that can now be run:")
    logger.info("1. Find all classes with their methods:")
    logger.info("""
    MATCH (c:Implementation {type: 'class'})-[:CONTAINS]->(m:Implementation {type: 'method'})
    RETURN c.name as Class, collect(m.name) as Methods
    """)
    
    logger.info("2. Find the function call hierarchy:")
    logger.info("""
    MATCH path = (f:Implementation {type: 'function'})-[:CALLS*1..3]->(called)
    WHERE f.name = 'main'
    RETURN path
    """)
    
    logger.info("3. Find all modules and their imports:")
    logger.info("""
    MATCH (m:Module)-[:IMPORTS]->(imported:Module)
    RETURN m.name as Module, collect(imported.name) as Imports
    """)

def main():
    """Main function demonstrating the Python Code Chunker usage."""
    logger.info("Starting Python Code Chunker example")
    
    # Create a temporary directory for the sample code
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.info(f"Created temporary directory: {temp_path}")
        
        # Create sample code files
        file_paths = create_sample_code(temp_path)
        logger.info(f"Created {len(file_paths)} sample Python files")
        
        # Initialize the code chunker
        chunker = PythonCodeChunker()
        
        # Analyze each file individually
        all_chunks = []
        for filename, file_path in file_paths.items():
            logger.info(f"\n--- Analyzing {filename} ---")
            chunks = analyze_single_file(chunker, file_path)
            all_chunks.extend(chunks)
        
        # Initialize Neo4j client and adapter
        # Note: In a real scenario, you would use actual Neo4j connection details
        try:
            neo4j_client = Neo4jClient(
                uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                username=os.environ.get("NEO4J_USERNAME", "neo4j"),
                password=os.environ.get("NEO4J_PASSWORD", "password")
            )
            adapter = ChunkGraphAdapter(neo4j_client=neo4j_client)
            
            # Build the knowledge graph
            logger.info("\n--- Building Knowledge Graph ---")
            build_knowledge_graph(chunker, adapter, temp_path)
            
            # Example queries on the knowledge graph
            logger.info("\n--- Querying the Knowledge Graph ---")
            
            # Find all classes
            classes = neo4j_client.query(
                "MATCH (c:Implementation {type: 'class'}) RETURN c.name as name"
            )
            logger.info(f"Classes in the codebase: {[cls['name'] for cls in classes]}")
            
            # Find methods of a specific class
            user_methods = neo4j_client.query(
                "MATCH (c:Implementation {type: 'class', name: 'User'})-[:CONTAINS]->(m:Implementation {type: 'method'}) "
                "RETURN m.name as name"
            )
            logger.info(f"Methods of User class: {[method['name'] for method in user_methods]}")
            
            # Find dependencies between files
            module_deps = neo4j_client.query(
                "MATCH (m:Module)-[:IMPORTS]->(imp:Module) "
                "RETURN m.name as module, collect(imp.name) as imports"
            )
            for dep in module_deps:
                logger.info(f"Module {dep['module']} imports: {dep['imports']}")
            
        except Exception as e:
            logger.warning(f"Skipping Neo4j operations: {str(e)}")
            logger.info("You can still examine the chunks that were generated.")
    
    logger.info("Python Code Chunker example completed")

if __name__ == "__main__":
    main() 