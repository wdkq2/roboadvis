import os
import json
from typing import List, Dict, Optional
import openai
from openai import OpenAI
import logging
from dotenv import load_dotenv

from embedding_manager import EmbeddingManager

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGChatbot:
    """RAG 기반 챗봇 클래스"""
    
    def __init__(self, 
                 embedding_manager: EmbeddingManager,
                 model_name: str = "gpt-3.5-turbo",
                 max_tokens: int = 1000,
                 temperature: float = 0.7):
        
        self.embedding_manager = embedding_manager
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # OpenAI 클라이언트 초기화
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=api_key)
        
        # 대화 히스토리
        self.conversation_history = []
        
        # 시스템 프롬프트
        self.system_prompt = """당신은 주택정책 전문가입니다. 
주택정책 보도자료와 관련된 질문에 대해 정확하고 도움이 되는 답변을 제공해주세요.

답변할 때 다음 원칙을 따라주세요:
1. 제공된 문서 내용을 기반으로 정확한 정보를 제공하세요
2. 문서에 없는 내용은 추측하지 말고 "문서에 해당 정보가 없습니다"라고 답변하세요
3. 답변은 한국어로 제공하세요
4. 복잡한 정책 내용은 이해하기 쉽게 설명하세요
5. 가능하면 구체적인 수치나 예시를 포함하세요

문서 내용:
{context}

질문: {question}"""
    
    def search_relevant_documents(self, query: str, n_results: int = 3) -> List[Dict]:
        """질문과 관련된 문서들을 검색합니다."""
        return self.embedding_manager.search_similar(query, n_results=n_results)
    
    def create_context_from_documents(self, documents: List[Dict]) -> str:
        """검색된 문서들로부터 컨텍스트를 생성합니다."""
        if not documents:
            return "관련 문서를 찾을 수 없습니다."
        
        context_parts = []
        for doc in documents:
            similarity = doc.get('similarity', 0)
            content = doc.get('document', '')
            metadata = doc.get('metadata', {})
            
            # 유사도가 높은 문서만 포함
            if similarity > 0.6:
                context_parts.append(f"[유사도: {similarity:.2f}] {content}")
        
        return "\n\n".join(context_parts) if context_parts else "관련 문서를 찾을 수 없습니다."
    
    def generate_response(self, question: str, context: str) -> str:
        """OpenAI API를 사용하여 답변을 생성합니다."""
        try:
            # 프롬프트 구성
            prompt = self.system_prompt.format(
                context=context,
                question=question
            )
            
            # 대화 히스토리 추가
            messages = [
                {"role": "system", "content": prompt}
            ]
            
            # 이전 대화 히스토리 추가 (최근 5개)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # 현재 질문 추가
            messages.append({"role": "user", "content": question})
            
            # API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answer = response.choices[0].message.content
            
            # 대화 히스토리에 추가
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # 히스토리 길이 제한 (메모리 관리)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return answer
            
        except Exception as e:
            logger.error(f"답변 생성 실패: {e}")
            return f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}"
    
    def chat(self, question: str) -> Dict:
        """챗봇과 대화합니다."""
        try:
            # 1. 관련 문서 검색
            relevant_docs = self.search_relevant_documents(question)
            
            # 2. 컨텍스트 생성
            context = self.create_context_from_documents(relevant_docs)
            
            # 3. 답변 생성
            answer = self.generate_response(question, context)
            
            # 4. 결과 반환
            result = {
                "question": question,
                "answer": answer,
                "relevant_documents": relevant_docs,
                "context_used": context,
                "model_used": self.model_name
            }
            
            logger.info(f"챗봇 응답 생성 완료: {len(answer)} 문자")
            return result
            
        except Exception as e:
            logger.error(f"챗봇 처리 실패: {e}")
            return {
                "question": question,
                "answer": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
                "relevant_documents": [],
                "context_used": "",
                "model_used": self.model_name
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """대화 히스토리를 반환합니다."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """대화 히스토리를 초기화합니다."""
        self.conversation_history = []
        logger.info("대화 히스토리가 초기화되었습니다.")
    
    def get_system_info(self) -> Dict:
        """시스템 정보를 반환합니다."""
        collection_info = self.embedding_manager.get_collection_info()
        
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "conversation_history_length": len(self.conversation_history),
            "embedding_collection": collection_info
        }