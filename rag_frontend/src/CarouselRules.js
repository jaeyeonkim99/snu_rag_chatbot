import React, { useState } from 'react';
import { Card, Button, Row, Col, Modal } from 'react-bootstrap';

const CarouselRules = ({ rules }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState('');

  const handleShow = (detail) => {
    setSelectedDetail(detail);
    setShowModal(true);
  };

  const handleClose = () => setShowModal(false);

  return (
    <div>
      <Row>
        {rules.filter(rule => rule.summary !== null && rule.detail !== null).map((rule, index) => (
          <Col key={index} md={4} style={{ marginBottom: '20px' }}>
            <Card style={{ height: '100%' }}>
              <Card.Body style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Card.Title>관련 학칙 {index + 1}</Card.Title>
                <Card.Text>{rule.summary}</Card.Text>
                <Button variant="primary" onClick={() => handleShow(rule.detail)}>
                  자세히 보기
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
      <Modal show={showModal} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>학칙 상세 내용</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>{selectedDetail}</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            닫기
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default CarouselRules;