# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Firebase Firestore Service Layer
Handles all database operations with async support
Provides CRUD operations for all collections
"""

import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID
import logging
from concurrent.futures import ThreadPoolExecutor
from firebase_admin import firestore

from app.config.firebase_config import get_firestore_client, Collections

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# BACKGROUND EXECUTOR FOR ASYNC FIRESTORE OPERATIONS
# ============================================================================

# Create a thread pool for running sync Firestore operations asynchronously
executor = ThreadPoolExecutor(max_workers=10)


# ============================================================================
# GENERIC FIRESTORE SERVICE
# ============================================================================

class FirestoreService:
    """
    Generic service layer for Firestore operations
    Provides CRUD methods for any collection
    """
    
    def __init__(self):
        """Initialize Firestore service"""
        self.db = get_firestore_client()
    
    # ========================================================================
    # CREATE OPERATIONS
    # ========================================================================
    
    async def create_document(
        self,
        collection: str,
        document_id: Optional[str] = None,
        data: Dict[str, Any] = None
    ) -> str:
        """
        Create a new document in Firestore
        
        Args:
            collection: Collection name (e.g., 'users', 'tickets')
            document_id: Optional custom document ID (auto-generated if not provided)
            data: Document data dictionary
            
        Returns:
            Document ID
            
        Raises:
            ValueError: If data is None or invalid
            Exception: Firestore write errors
        """
        try:
            if data is None:
                raise ValueError("Document data cannot be None")
            
            # Run sync operation in executor for async compatibility
            loop = asyncio.get_event_loop()
            
            if document_id:
                # Set document with specific ID
                await loop.run_in_executor(
                    executor,
                    lambda: self.db.collection(collection).document(document_id).set(data)
                )
                logger.info(f"✅ Created document: {collection}/{document_id}")
                return document_id
            else:
                # Auto-generate document ID
                ref = await loop.run_in_executor(
                    executor,
                    lambda: self.db.collection(collection).add(data)
                )
                doc_id = ref[1].id
                logger.info(f"✅ Created document: {collection}/{doc_id}")
                return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to create document in {collection}: {str(e)}")
            raise
    
    # ========================================================================
    # READ OPERATIONS
    # ========================================================================
    
    async def get_document(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single document from Firestore
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            Document data with 'id' field, or None if not found
        """
        try:
            loop = asyncio.get_event_loop()
            
            doc = await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).get()
            )
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                logger.info(f"✅ Retrieved document: {collection}/{document_id}")
                return data
            else:
                logger.warning(f"⚠️ Document not found: {collection}/{document_id}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve document: {str(e)}")
            raise
    
    async def get_all_documents(
        self,
        collection: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all documents from a collection
        
        Args:
            collection: Collection name
            limit: Maximum number of documents to retrieve
            
        Returns:
            List of documents with 'id' field
        """
        try:
            loop = asyncio.get_event_loop()
            
            def fetch_docs():
                query = self.db.collection(collection)
                if limit:
                    query = query.limit(limit)
                return query.stream()
            
            docs_stream = await loop.run_in_executor(executor, fetch_docs)
            
            documents = []
            for doc in docs_stream:
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            logger.info(f"✅ Retrieved {len(documents)} documents from {collection}")
            return documents
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve documents from {collection}: {str(e)}")
            raise
    
    async def query_documents(
        self,
        collection: str,
        field: str,
        operator: str,
        value: Any,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents using a single filter
        
        Args:
            collection: Collection name
            field: Field name to filter on
            operator: Comparison operator ('==', '<', '>', '<=', '>=', '!=')
            value: Value to compare against
            limit: Maximum number of results
            
        Returns:
            List of matching documents with 'id' field
        """
        try:
            loop = asyncio.get_event_loop()
            
            def perform_query():
                query = self.db.collection(collection).where(field, operator, value)
                if limit:
                    query = query.limit(limit)
                return query.stream()
            
            docs_stream = await loop.run_in_executor(executor, perform_query)
            
            documents = []
            for doc in docs_stream:
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            logger.info(f"✅ Query returned {len(documents)} documents from {collection}")
            return documents
        
        except Exception as e:
            logger.error(f"❌ Query failed on {collection}: {str(e)}")
            raise
    
    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================
    
    async def update_document(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update a document in Firestore
        
        Args:
            collection: Collection name
            document_id: Document ID
            data: Data to update (will merge with existing if merge=True)
            merge: If True, merge with existing data; if False, replace entire doc
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Add timestamp
            data['updated_at'] = datetime.now()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).set(
                    data,
                    merge=merge
                )
            )
            
            logger.info(f"✅ Updated document: {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to update document: {str(e)}")
            raise
    
    async def increment_field(
        self,
        collection: str,
        document_id: str,
        field: str,
        value: int = 1
    ) -> bool:
        """
        Increment a numeric field (useful for counters)
        
        Args:
            collection: Collection name
            document_id: Document ID
            field: Field name to increment
            value: Amount to increment by
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).update({
                    field: firestore.Increment(value)
                })
            )
            
            logger.info(f"✅ Incremented {field} in {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to increment field: {str(e)}")
            raise
    
    async def add_to_array(
        self,
        collection: str,
        document_id: str,
        field: str,
        value: Any
    ) -> bool:
        """
        Add an element to an array field
        
        Args:
            collection: Collection name
            document_id: Document ID
            field: Array field name
            value: Value to append
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).update({
                    field: firestore.ArrayUnion([value])
                })
            )
            
            logger.info(f"✅ Added to array {field} in {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to add to array: {str(e)}")
            raise
    
    async def remove_from_array(
        self,
        collection: str,
        document_id: str,
        field: str,
        value: Any
    ) -> bool:
        """
        Remove an element from an array field
        
        Args:
            collection: Collection name
            document_id: Document ID
            field: Array field name
            value: Value to remove
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).update({
                    field: firestore.ArrayRemove([value])
                })
            )
            
            logger.info(f"✅ Removed from array {field} in {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to remove from array: {str(e)}")
            raise
    
    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================
    
    async def delete_document(
        self,
        collection: str,
        document_id: str
    ) -> bool:
        """
        Delete a document from Firestore
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).delete()
            )
            
            logger.info(f"✅ Deleted document: {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete document: {str(e)}")
            raise
    
    async def delete_field(
        self,
        collection: str,
        document_id: str,
        field: str
    ) -> bool:
        """
        Delete a specific field from a document
        
        Args:
            collection: Collection name
            document_id: Document ID
            field: Field name to delete
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                executor,
                lambda: self.db.collection(collection).document(document_id).update({
                    field: firestore.DELETE_FIELD
                })
            )
            
            logger.info(f"✅ Deleted field {field} from {collection}/{document_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete field: {str(e)}")
            raise
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    async def batch_create(
        self,
        collection: str,
        documents: List[tuple]  # List of (doc_id, data) or (None, data) for auto-ID
    ) -> List[str]:
        """
        Create multiple documents in a batch operation
        
        Args:
            collection: Collection name
            documents: List of tuples (document_id, data)
            
        Returns:
            List of created document IDs
        """
        try:
            loop = asyncio.get_event_loop()
            
            def perform_batch():
                batch = self.db.batch()
                doc_ids = []
                
                for doc_id, data in documents:
                    if doc_id is None:
                        # Auto-generate ID
                        doc_id = self.db.collection(collection).document().id
                    
                    batch.set(
                        self.db.collection(collection).document(doc_id),
                        data
                    )
                    doc_ids.append(doc_id)
                
                batch.commit()
                return doc_ids
            
            doc_ids = await loop.run_in_executor(executor, perform_batch)
            logger.info(f"✅ Batch created {len(doc_ids)} documents in {collection}")
            return doc_ids
        
        except Exception as e:
            logger.error(f"❌ Batch create failed: {str(e)}")
            raise
    
    async def batch_update(
        self,
        collection: str,
        updates: Dict[str, Dict[str, Any]]  # {doc_id: {field: value}}
    ) -> bool:
        """
        Update multiple documents in a batch operation
        
        Args:
            collection: Collection name
            updates: Dictionary mapping doc_id to update data
            
        Returns:
            True if successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            def perform_batch():
                batch = self.db.batch()
                
                for doc_id, data in updates.items():
                    data['updated_at'] = datetime.now()
                    batch.update(
                        self.db.collection(collection).document(doc_id),
                        data
                    )
                
                batch.commit()
            
            await loop.run_in_executor(executor, perform_batch)
            logger.info(f"✅ Batch updated {len(updates)} documents in {collection}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Batch update failed: {str(e)}")
            raise


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_firestore_service: Optional[FirestoreService] = None


def get_firestore_service() -> FirestoreService:
    """Get or create Firestore service singleton"""
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service
