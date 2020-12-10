import React, { Component, useState, useEffect, useLayoutEffect} from 'react';
import { Button, Grid, Col, ControlLabel, Form, FormGroup } from 'react-bootstrap';
import { Input} from 'reactstrap';
import axios from 'axios';

export default function JoinServer (){
    const [node_ip, setNodeip] = useState('');
    const [node_port, setNodePort] = useState('');
    const [server_port, setServerPort] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        console.log(sessionStorage);
      }, []);

      let handleUserChangeIP = (evt) => {
        setNodeip(evt.target.value);
      };
      let handleUserChangePort = (evt) => {
        setNodePort(evt.target.value);
      };
      let handleUserChangeServer = (evt) => {
        setServerPort(evt.target.value);
      };

      let checkFields = () => {
        var count = 0;
        if (!node_ip || !node_port || !server_port) {
          count++;
        }
    }

      let handleSubmit = (evt) => {
        evt.preventDefault();
    
        if(checkFields() > 0){
          setMessage('Fill all required fields!');
          return;
        }
    
        sessionStorage.setItem('server_port', server_port);

    
        console.log(server_port)
        var query = 'http://localhost:'+server_port+'/connect';
    
        axios.post((query), {
            ip: node_ip,
            port: node_port
        })
        .then(response => {
            console.log(response);
            if(response.data.success === "success") {
              window.location.reload();
            }
        })
        .catch(error => console.log(error));
    
      }




      return (
        <div className={'App'}>
            <Col className="rows">
              <div className="Login">
                <h2 align = "center">Join</h2>
                <Form horizontal>
  
                    <Form.Group className="formHorizontal">
                    <Form.Label  >
                      IP
                    </Form.Label>
                      <Col >                      
                        <Input
                            name="node_ip"
                            id="node_ip"
                            value={node_ip}
                            onChange={handleUserChangeIP}
                        />
                      </Col>

                    <Form.Label  >
                      Port
                    </Form.Label>
                      <Col >                      
                        <Input
                            name="node_port"
                            id="node_port"
                            value={node_port}
                            onChange={handleUserChangePort}
                        />
                      </Col>

                    <Form.Label  >
                      Server Port
                    </Form.Label>
                      <Col >                      
                        <Input
                            name="server_port"
                            id="server_port"
                            value={server_port}
                            onChange={handleUserChangeServer}
                        />
                      </Col>
                    </Form.Group>
                    <h5 align = "center">{message}</h5>
                    <p className="buttons button" align='center'>
                      <Button variant="outline-info" onClick={handleSubmit}>Start</Button>
                    </p>
  
                </Form>
              </div>
            </Col>
        </div>
      )

}
