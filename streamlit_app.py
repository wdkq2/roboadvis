import streamlit as st
import os
import sys
from typing import List, Dict
import json
from datetime import datetime

# 프로젝트 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor
from embedding_manager import EmbeddingManager
from rag_chatbot import RAGChatbot
from data_collector import DataCollector

# 페이지 설정
st.set_page_config(
    page_title="🏠 주택정책 RAG 챗봇",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .info-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_chatbot():
    """챗봇을 초기화합니다."""
    try:
        pdf_processor = PDFProcessor()
        embedding_manager = EmbeddingManager()
        chatbot = RAGChatbot(embedding_manager)
        data_collector = DataCollector()
        
        return {
            'pdf_processor': pdf_processor,
            'embedding_manager': embedding_manager,
            'chatbot': chatbot,
            'data_collector': data_collector
        }
    except Exception as e:
        st.error(f"챗봇 초기화 실패: {e}")
        return None

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.markdown('<h1 class="main-header">🏠 주택정책 RAG 챗봇</h1>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API 키 확인
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            st.stop()
        else:
            st.success("✅ API 키가 설정되었습니다.")
        
        # 시스템 정보
        st.subheader("📊 시스템 정보")
        
        # 챗봇 초기화
        chatbot_components = initialize_chatbot()
        if chatbot_components is None:
            st.error("챗봇 초기화에 실패했습니다.")
            st.stop()
        
        chatbot = chatbot_components['chatbot']
        embedding_manager = chatbot_components['embedding_manager']
        
        # 컬렉션 정보
        collection_info = embedding_manager.get_collection_info()
        doc_count = collection_info.get('document_count', 0)
        
        st.metric("문서 수", doc_count)
        st.metric("모델", chatbot.model_name)
        
        # 데이터베이스 구축 버튼
        st.subheader("🔧 데이터베이스 관리")
        
        if st.button("📚 데이터베이스 구축", type="primary"):
            with st.spinner("데이터베이스를 구축하는 중..."):
                try:
                    # 샘플 PDF URL들 (실제로는 공공데이터 포탈에서 수집)
                    sample_urls = [
                        "https://www.molit.go.kr/news/news_list.jsp?news_type=news&page=1"
                    ]
                    
                    success = setup_database(chatbot_components, sample_urls)
                    if success:
                        st.success("✅ 데이터베이스 구축이 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 데이터베이스 구축에 실패했습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
        
        # 대화 히스토리 초기화
        if st.button("🗑️ 대화 히스토리 초기화"):
            chatbot.clear_conversation_history()
            st.success("대화 히스토리가 초기화되었습니다!")
            st.rerun()
        
        # 파일 업로드
        st.subheader("📁 PDF 파일 업로드")
        uploaded_files = st.file_uploader(
            "PDF 파일을 선택하세요",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("📤 파일 처리"):
            with st.spinner("PDF 파일을 처리하는 중..."):
                try:
                    success = process_uploaded_files(chatbot_components, uploaded_files)
                    if success:
                        st.success("✅ 파일 처리가 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 파일 처리에 실패했습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
    
    # 메인 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 주택정책 질문하기")
        
        # 채팅 인터페이스
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 이전 메시지들 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 사용자 입력
        if prompt := st.chat_input("주택정책에 대해 질문해주세요..."):
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 챗봇 응답
            with st.chat_message("assistant"):
                with st.spinner("답변을 생성하는 중..."):
                    try:
                        result = chatbot.chat(prompt)
                        response = result['answer']
                        
                        st.markdown(response)
                        
                        # 관련 문서 정보
                        if result['relevant_documents']:
                            with st.expander(f"📚 참고 문서 ({len(result['relevant_documents'])}개)"):
                                for i, doc in enumerate(result['relevant_documents'][:3], 1):
                                    similarity = doc.get('similarity', 0)
                                    metadata = doc.get('metadata', {})
                                    filename = metadata.get('filename', '알 수 없음')
                                    st.write(f"**{i}. {filename}** (유사도: {similarity:.2f})")
                                    st.text(doc.get('document', '')[:200] + "...")
                        
                        # 어시스턴트 메시지 추가
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    with col2:
        st.subheader("💡 질문 예시")
        
        example_questions = [
            "주택정책의 주요 내용은 무엇인가요?",
            "최근 주택정책 변경사항이 있나요?",
            "주택정책의 목표는 무엇인가요?",
            "주택정책이 일반 시민에게 미치는 영향은 무엇인가요?",
            "주택정책의 효과는 어떻게 측정되나요?",
            "주택정책의 문제점은 무엇인가요?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        st.subheader("📋 대화 히스토리")
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages[-5:], 1):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                st.write(f"{i}. {role_icon} {msg['content'][:50]}...")
        else:
            st.write("아직 대화가 없습니다.")

def setup_database(chatbot_components: Dict, pdf_urls: List[str]) -> bool:
    """데이터베이스를 구축합니다."""
    try:
        pdf_processor = chatbot_components['pdf_processor']
        embedding_manager = chatbot_components['embedding_manager']
        
        processed_chunks = []
        
        for i, url in enumerate(pdf_urls):
            try:
                # PDF 다운로드
                filename = f"housing_policy_{i+1}.pdf"
                pdf_path = pdf_processor.download_pdf_from_url(url, filename)
                
                if pdf_path:
                    # 텍스트 추출 및 청킹
                    chunks = pdf_processor.process_pdf_file(pdf_path)
                    
                    # 메타데이터 추가
                    metadata = pdf_processor.get_pdf_metadata(pdf_path)
                    metadata['source_url'] = url
                    metadata['filename'] = filename
                    
                    # 임베딩 데이터베이스에 추가
                    if chunks:
                        success = embedding_manager.add_documents(
                            texts=chunks,
                            metadata=[metadata] * len(chunks)
                        )
                        
                        if success:
                            processed_chunks.extend(chunks)
                
            except Exception as e:
                st.error(f"PDF 처리 실패: {url} - {e}")
                continue
        
        return len(processed_chunks) > 0
        
    except Exception as e:
        st.error(f"데이터베이스 구축 실패: {e}")
        return False

def process_uploaded_files(chatbot_components: Dict, uploaded_files) -> bool:
    """업로드된 파일들을 처리합니다."""
    try:
        pdf_processor = chatbot_components['pdf_processor']
        embedding_manager = chatbot_components['embedding_manager']
        
        processed_chunks = []
        
        for uploaded_file in uploaded_files:
            try:
                # 파일 저장
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 텍스트 추출 및 청킹
                chunks = pdf_processor.process_pdf_file(file_path)
                
                # 메타데이터 추가
                metadata = {
                    'filename': uploaded_file.name,
                    'file_size': uploaded_file.size,
                    'upload_time': datetime.now().isoformat()
                }
                
                # 임베딩 데이터베이스에 추가
                if chunks:
                    success = embedding_manager.add_documents(
                        texts=chunks,
                        metadata=[metadata] * len(chunks)
                    )
                    
                    if success:
                        processed_chunks.extend(chunks)
                
                # 임시 파일 삭제
                os.remove(file_path)
                
            except Exception as e:
                st.error(f"파일 처리 실패: {uploaded_file.name} - {e}")
                continue
        
        return len(processed_chunks) > 0
        
    except Exception as e:
        st.error(f"파일 처리 실패: {e}")
        return False

if __name__ == "__main__":
    main()