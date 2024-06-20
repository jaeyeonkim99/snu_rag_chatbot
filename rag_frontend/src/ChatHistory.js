import React, { useEffect, useRef } from 'react';
import { Row, Col, Card, Container, Spinner } from 'react-bootstrap';
import './ChatHistory.css';
import CarouselRules from './CarouselRules';

const ChatHistory = ({ chatHistory, loadingItemId }) => {
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  return (
    <Container>
      {chatHistory.map((chat) => (
        <div key={chat.id} className="mb-4">
          <div className="d-flex justify-content-end mb-2">
            <Card className="chat-bubble answer-bubble">
              {chat.question ? (
                <Card.Body>
                  <Card.Text>
                    {chat.question}
                  </Card.Text>
                </Card.Body>
              ) : null}
            </Card>
          </div>
          <Row className="mt-4">
            <Col>
              <CarouselRules rules={chat.rules} />
            </Col>
          </Row>
          <div className="d-flex justify-content-start mb-2">
            <Card className="chat-bubble question-bubble">
              {chat.answer ? (
                <Card.Body>
                  <Card.Text>
                    {chat.answer}
                  </Card.Text>
                </Card.Body>
              ) : (
                <Card.Body>
                  <Spinner animation='border'></Spinner>
                </Card.Body>
              )}
            </Card>
          </div>
        </div>
      ))}
      <div ref={chatEndRef} />
    </Container>
  );
};

export default ChatHistory;
