import React from 'react';
import { Form, Button, Col, Row } from 'react-bootstrap';


const handleSubmit = (e, handleQuestionSubmit) => {
  e.preventDefault();
  handleQuestionSubmit();
};

const QuestionBox = ({ question, setQuestion, handleQuestionSubmit }) => (
  <Form>
    <Row>
      <Col md={10}>
        <Form.Control
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSubmit(e, handleQuestionSubmit);
            }
          }}
        />
      </Col>
      <Col md={2}>
        <Button onClick={handleQuestionSubmit} style={{ width: '100%' }}>질문하기</Button>
      </Col>
    </Row>
  </Form>
);

export default QuestionBox;