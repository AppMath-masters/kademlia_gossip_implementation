import React, { Component, useState, useEffect, useLayoutEffect} from 'react';
import { Button, Grid, Col, ControlLabel, Form, FormGroup } from 'react-bootstrap';
import { Input} from 'reactstrap';
import axios from 'axios';

export default function SearchFile (){
    const [name, setName] = useState('');
    const [message, setMessage] = useState('');
    const port = sessionStorage.getItem('server_port')
    const [id_array, setArray] = useState('');
    const [file_id, setFile_id] = useState('');



    useEffect(() => {
      console.log(sessionStorage);
    }, []);

    let handleUserChangeName = (evt) => {
        setName(evt.target.value);
      };

    let checkFields = () => {
        var count = 0;
        if (!name) {
          count++;
        }
    }

    let handleSubmit = (event) => {
        if(checkFields() > 0){
            setMessage('Fill all required fields!');
            return;
          }

        event.preventDefault();

        var query = 'http://localhost:'+port+'/search';
    
        axios.post((query), {
            name: name
        })
        .then(response => {
            console.log(response);
            /*
            setFile_id(response.id);
            if (sessionStorage.getItem('id_array') == undefined) {
              sessionStorage.setItem('id_array', file_id);
            } 
            else{
              id_array = sessionStorage.getItem('id_array')
              id_array = id_array.push(file_id)
              sessionStorage.setItem('id_array', id_array);
            }
            */

              
        })
        .catch(error => console.log(error));
    
    }

    return (
        <div className={'App'}>
            <Col className="rows">
              <div className="Login">
                <h1 align = "center">Search for file</h1>
                <Form horizontal>
  
                    <Form.Group className="formHorizontal">
                    <Form.Label  >
                      IP
                    </Form.Label>
                      <Col >                      
                        <Input
                            name="name"
                            id="name"
                            value={name}
                            onChange={handleUserChangeName}
                        />
                      </Col>

                    
                    </Form.Group>
                    <h5 align = "center">{message}</h5>
                    <p className="buttons button" align='center'>
                      <Button variant="outline-info" onClick={handleSubmit}>Search</Button>
                    </p>
  
                </Form>
              </div>
            </Col>
        </div>
      )
}