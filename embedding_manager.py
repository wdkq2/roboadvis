import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingManager:
    """텍스트 임베딩과 벡터 데이터베이스를 관리하는 클래스"""
    
    def __init__(self, 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 db_path: str = "chroma_db",
                 collection_name: str = "housing_policy_docs"):
        
        self.model_name = model_name
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Sentence Transformer 모델 로드
        logger.info(f"임베딩 모델 로드 중: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 컬렉션 가져오기 또는 생성
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"기존 컬렉션 로드: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "주택정책 보도자료 임베딩"}
            )
            logger.info(f"새 컬렉션 생성: {collection_name}")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """텍스트 리스트를 임베딩합니다."""
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            logger.info(f"{len(texts)}개 텍스트 임베딩 완료")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            return []
    
    def add_documents(self, 
                     texts: List[str], 
                     metadata: Optional[List[Dict]] = None,
                     ids: Optional[List[str]] = None) -> bool:
        """문서들을 벡터 데이터베이스에 추가합니다."""
        try:
            if not texts:
                logger.warning("추가할 텍스트가 없습니다.")
                return False
            
            # 임베딩 생성
            embeddings = self.create_embeddings(texts)
            if not embeddings:
                return False
            
            # ID 생성
            if ids is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ids = [f"doc_{timestamp}_{i}" for i in range(len(texts))]
            
            # 메타데이터 설정
            if metadata is None:
                metadata = [{"source": "housing_policy", "timestamp": timestamp} for _ in texts]
            
            # 컬렉션에 추가
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"{len(texts)}개 문서를 벡터 데이터베이스에 추가했습니다.")
            return True
            
        except Exception as e:
            logger.error(f"문서 추가 실패: {e}")
            return False
    
    def search_similar(self, 
                      query: str, 
                      n_results: int = 5,
                      threshold: float = 0.5) -> List[Dict]:
        """쿼리와 유사한 문서들을 검색합니다."""
        try:
            # 쿼리 임베딩
            query_embedding = self.embedding_model.encode([query])
            
            # 유사도 검색
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # 결과 처리
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # 거리를 유사도로 변환 (ChromaDB는 거리를 반환하므로)
                    similarity = 1 - distance
                    
                    if similarity >= threshold:
                        similar_docs.append({
                            'document': doc,
                            'metadata': metadata,
                            'similarity': similarity,
                            'rank': i + 1
                        })
            
            logger.info(f"검색 결과: {len(similar_docs)}개 문서 발견")
            return similar_docs
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def get_collection_info(self) -> Dict:
        """컬렉션 정보를 반환합니다."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "model_name": self.model_name,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"컬렉션 정보 조회 실패: {e}")
            return {}
    
    def delete_collection(self) -> bool:
        """컬렉션을 삭제합니다."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"컬렉션 삭제 완료: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"컬렉션 삭제 실패: {e}")
            return False
    
    def update_document(self, 
                       doc_id: str, 
                       new_text: str, 
                       new_metadata: Optional[Dict] = None) -> bool:
        """문서를 업데이트합니다."""
        try:
            # 새 임베딩 생성
            new_embedding = self.embedding_model.encode([new_text])
            
            # 업데이트
            self.collection.update(
                ids=[doc_id],
                embeddings=new_embedding.tolist(),
                documents=[new_text],
                metadatas=[new_metadata] if new_metadata else None
            )
            
            logger.info(f"문서 업데이트 완료: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"문서 업데이트 실패: {e}")
            return False