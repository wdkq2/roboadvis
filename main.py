#!/usr/bin/env python3
"""
주택정책 RAG 챗봇 메인 실행 파일
"""

import os
import sys
import logging
from typing import List, Dict
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from embedding_manager import EmbeddingManager
from rag_chatbot import RAGChatbot
from data_collector import DataCollector

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HousingPolicyChatbot:
    """주택정책 RAG 챗봇 메인 클래스"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedding_manager = EmbeddingManager()
        self.chatbot = RAGChatbot(self.embedding_manager)
        self.data_collector = DataCollector()
        
        logger.info("주택정책 RAG 챗봇 초기화 완료")
    
    def setup_database(self, pdf_urls: List[str] = None):
        """PDF 데이터를 수집하고 벡터 데이터베이스를 구축합니다."""
        try:
            if pdf_urls is None:
                # 공공데이터 포탈에서 PDF 수집
                logger.info("공공데이터 포탈에서 PDF 수집 중...")
                pdf_info = self.data_collector.search_housing_policy_pdfs()
                
                if not pdf_info:
                    logger.warning("PDF를 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
                    pdf_urls = self.data_collector.get_sample_pdf_urls()
                else:
                    pdf_urls = [info['pdf_url'] for info in pdf_info if info.get('pdf_url')]
            
            if not pdf_urls:
                logger.error("처리할 PDF가 없습니다.")
                return False
            
            # PDF 다운로드 및 처리
            processed_chunks = []
            
            for i, url in enumerate(pdf_urls):
                try:
                    logger.info(f"PDF 처리 중 ({i+1}/{len(pdf_urls)}): {url}")
                    
                    # PDF 다운로드
                    filename = f"housing_policy_{i+1}.pdf"
                    pdf_path = self.pdf_processor.download_pdf_from_url(url, filename)
                    
                    if pdf_path:
                        # 텍스트 추출 및 청킹
                        chunks = self.pdf_processor.process_pdf_file(pdf_path)
                        
                        # 메타데이터 추가
                        metadata = self.pdf_processor.get_pdf_metadata(pdf_path)
                        metadata['source_url'] = url
                        metadata['filename'] = filename
                        
                        # 임베딩 데이터베이스에 추가
                        if chunks:
                            success = self.embedding_manager.add_documents(
                                texts=chunks,
                                metadata=[metadata] * len(chunks)
                            )
                            
                            if success:
                                processed_chunks.extend(chunks)
                                logger.info(f"PDF 처리 완료: {len(chunks)}개 청크")
                            else:
                                logger.error(f"PDF 임베딩 실패: {filename}")
                        else:
                            logger.warning(f"PDF에서 텍스트를 추출할 수 없습니다: {filename}")
                    
                except Exception as e:
                    logger.error(f"PDF 처리 실패: {url} - {e}")
                    continue
            
            logger.info(f"총 {len(processed_chunks)}개 청크를 처리했습니다.")
            return len(processed_chunks) > 0
            
        except Exception as e:
            logger.error(f"데이터베이스 구축 실패: {e}")
            return False
    
    def chat_interface(self):
        """대화형 인터페이스를 제공합니다."""
        print("\n" + "="*60)
        print("🏠 주택정책 RAG 챗봇에 오신 것을 환영합니다! 🏠")
        print("="*60)
        print("주택정책과 관련된 질문을 해주세요.")
        print("종료하려면 'quit', 'exit', '종료'를 입력하세요.")
        print("대화 히스토리를 초기화하려면 'clear'를 입력하세요.")
        print("="*60)
        
        while True:
            try:
                # 사용자 입력
                user_input = input("\n질문: ").strip()
                
                if not user_input:
                    continue
                
                # 종료 명령
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print("챗봇을 종료합니다. 감사합니다!")
                    break
                
                # 히스토리 초기화
                if user_input.lower() == 'clear':
                    self.chatbot.clear_conversation_history()
                    print("대화 히스토리가 초기화되었습니다.")
                    continue
                
                # 시스템 정보
                if user_input.lower() == 'info':
                    info = self.chatbot.get_system_info()
                    print(f"\n📊 시스템 정보:")
                    print(f"모델: {info['model_name']}")
                    print(f"문서 수: {info['embedding_collection'].get('document_count', 0)}")
                    print(f"대화 히스토리: {info['conversation_history_length']}개")
                    continue
                
                # 챗봇 응답
                print("\n🤖 챗봇이 답변을 생성하는 중...")
                result = self.chatbot.chat(user_input)
                
                print(f"\n답변: {result['answer']}")
                
                # 관련 문서 정보 표시
                if result['relevant_documents']:
                    print(f"\n📚 참고 문서 ({len(result['relevant_documents'])}개):")
                    for i, doc in enumerate(result['relevant_documents'][:3], 1):
                        similarity = doc.get('similarity', 0)
                        metadata = doc.get('metadata', {})
                        filename = metadata.get('filename', '알 수 없음')
                        print(f"  {i}. {filename} (유사도: {similarity:.2f})")
                
            except KeyboardInterrupt:
                print("\n\n챗봇을 종료합니다. 감사합니다!")
                break
            except Exception as e:
                logger.error(f"대화 중 오류 발생: {e}")
                print(f"죄송합니다. 오류가 발생했습니다: {e}")
    
    def run_demo(self):
        """데모 모드로 실행합니다."""
        demo_questions = [
            "주택정책의 주요 내용은 무엇인가요?",
            "최근 주택정책 변경사항이 있나요?",
            "주택정책의 목표는 무엇인가요?",
            "주택정책이 일반 시민에게 미치는 영향은 무엇인가요?"
        ]
        
        print("\n" + "="*60)
        print("🎯 주택정책 RAG 챗봇 데모 모드")
        print("="*60)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n질문 {i}: {question}")
            print("-" * 40)
            
            result = self.chatbot.chat(question)
            print(f"답변: {result['answer']}")
            
            if result['relevant_documents']:
                print(f"참고 문서: {len(result['relevant_documents'])}개")
            
            print()

def main():
    """메인 함수"""
    try:
        # API 키 확인
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            print("환경변수 파일(.env)을 확인해주세요.")
            return
        
        # 챗봇 초기화
        chatbot = HousingPolicyChatbot()
        
        # 명령행 인수 처리
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "setup":
                print("🔧 데이터베이스 구축을 시작합니다...")
                success = chatbot.setup_database()
                if success:
                    print("✅ 데이터베이스 구축이 완료되었습니다.")
                else:
                    print("❌ 데이터베이스 구축에 실패했습니다.")
                return
            
            elif command == "demo":
                chatbot.run_demo()
                return
        
        # 기본 모드: 데이터베이스 확인 후 대화 시작
        collection_info = chatbot.embedding_manager.get_collection_info()
        doc_count = collection_info.get('document_count', 0)
        
        if doc_count == 0:
            print("📚 데이터베이스가 비어있습니다. 먼저 데이터를 수집하겠습니다...")
            success = chatbot.setup_database()
            if not success:
                print("❌ 데이터 수집에 실패했습니다. 데모 모드로 실행합니다.")
                chatbot.run_demo()
                return
        
        # 대화 인터페이스 시작
        chatbot.chat_interface()
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
        print(f"❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()