import React, { Component, useState, useEffect, useLayoutEffect, useRef} from 'react';
import { Button, Grid, Col, ControlLabel, Form, FormGroup } from 'react-bootstrap';
import { Input} from 'reactstrap';
import axios from 'axios';

export default function SearchFile (){
    const [name, setName] = useState('');
    const [message, setMessage] = useState('');
    const port = sessionStorage.getItem('server_port')
    
    const id_array = useRef([]);
    // const [file_id, setFile_id] = useState('');

		useEffect(() => {
      let stored = sessionStorage.getItem('id_array');
      if (stored) {
        id_array.current = stored;
      }
    }, []);

  	const requestSpamer = () => {
      fetch('http://localhost:8471/findresults', {
    		method: 'GET',
    		headers: {
      		'Content-Type': 'application/json'
    		},
    		body: JSON.stringify({
      		'ids': id_array.current
    		})
  		}).then(response => {
        for (let item in response.data) {
          if (item.name && item.path) {
            alert("Received file" + item.name + " " + item.path);
            id_array.current.splice(id_array.current.indexOf(item.id), 1);
            console.log(response.data);
            sessionStorage.setItem('id_array', id_array.current);
          }
        }
      }).catch(error => console.log(error));
    }
  
  	useEffect(() => {
      setInterval(requestSpamer, 5000)
    }, [])
  

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
            id_array.current.push(response.id);
      			sessionStorage.setItem('id_array', id_array.current);
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
                      File name
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