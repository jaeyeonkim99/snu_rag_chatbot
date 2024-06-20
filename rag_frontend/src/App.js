import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col } from 'react-bootstrap';
import axios from 'axios';
import QuestionBox from './QuestionBox';
import ChatHistory from './ChatHistory';
import seoulNationalLogo from './img.png';

function App() {
  const initialChatHistory = [
    {
      id: 0,
      question: "",
      answer: "안녕하세요? 무엇을 도와드릴까요?",
      rules: []
    }
  ];

  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState(initialChatHistory);
  const [loadingItemId, setLoadingItemId] = useState(null);

  async function handleQuestionSubmit() {
    try {
      const newId = Date.now();
      setLoadingItemId(newId);
      setQuestion('');
      const updatedChatHistory = [...chatHistory, { id: newId, question, answer: "", rules: [] }];
      setChatHistory(updatedChatHistory);
      const url = `http://localhost:8000/rag/?query=${encodeURIComponent(question)}`;
      const response = await axios.get(url, { timeout: 200000 });
      const { answer, rules } = response.data;

      const updatedChatHistory2 = [...chatHistory, { id: newId, question, answer: answer, rules: rules }];
      setChatHistory(updatedChatHistory2);
    } catch (error) {
      console.error('Fetch Error', error);
    } finally {
      setLoadingItemId(null);
    }
  };

  return (
    <Container style={{ fontFamily: 'Arial, Helvetica, sans-serif' }}>
      <Row className="mt-4 align-items-center">
        <Col xs={8}>
          <h1 className="font-weight-bold">서울대학교 학칙 챗봇</h1>
        </Col>
        <Col xs={4} className="d-flex justify-content-end">
          <img src={seoulNationalLogo} alt="서울대 마크" style={{ maxWidth: '100%', height: 'auto', maxHeight: '100px' }} />
        </Col>
      </Row>
      <Row className="mt-4">
        <Col>
          <div style={{ minHeight: '300px', maxHeight: 'calc(100vh - 250px)', overflowY: 'auto', border: '1px solid #ccc', borderRadius: '5px', padding: '15px' }}>
            <ChatHistory chatHistory={chatHistory} loadingItemId={loadingItemId} />
          </div>
        </Col>
      </Row>
      <Row className="mt-4">
        <Col>
          <QuestionBox
            question={question}
            setQuestion={setQuestion}
            handleQuestionSubmit={handleQuestionSubmit}
          />
        </Col>
      </Row>
    </Container>
  );
}

export default App;