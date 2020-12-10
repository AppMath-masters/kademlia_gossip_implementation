import React, { Component, useState, useEffect, useLayoutEffect} from 'react';
import { Button, Row, Col, ControlLabel, Form, FormGroup, Modal, ButtonToolbar } from 'react-bootstrap';
import axios from 'axios';

export default function AddFileModal() {

    const port = sessionStorage.getItem('server_port')
    const [show, setShow] = useState(false);
    const [name, setName] = useState('');
    const [path, setPath] = useState('');



    let handleSubmit = (event) => {

        event.preventDefault();

        var query = 'http://localhost:'+port+'/add';
    
        axios.post((query), {
            name: name,
            path: path
        })
        .then(response => {
            console.log(response);
              window.location.reload();
        })
        .catch(error => console.log(error));
    
    }

    let handleClose = () => {
      setShow(false);
    }
  
      return (
        <div>
          <Button  variant="outline-info" onClick={(e) => setShow(!show)}>
            Add new file
          </Button>
  
          <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Add new file to system</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            <Form className={'modal_form'}>
            <Form.Group as={Row} controlId="formHorizontalEmail">
                <Form.Label column sm={2}>
                    Name
                </Form.Label>
                <Col>
                    <Form.Control className={"select service modal_form"}  as="textarea" rows="1" required onChange={(e) => setName(e.target.value)}/>
                </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="formHorizontalEmail">
                <Form.Label column sm={2}>
                  Path
                </Form.Label>
                <Col>
                    <Form.Control className={"select service modal_form"}  as="textarea" rows="1" required onChange={(e) => setPath(e.target.value)}/>
                </Col>
            </Form.Group>
            

        </Form>     
            </Modal.Body>
            <Modal.Footer>
              <Button  variant="outline-info" onClick={handleSubmit}>
                Save
              </Button>
              <Button variant="secondary" onClick={handleClose}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
      );
  }
  
