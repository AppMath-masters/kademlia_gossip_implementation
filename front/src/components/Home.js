import React from 'react'
import { Redirect } from 'react-router-dom';
import JoinServer from './JoinServer';
import TableNodes from './TableNodes';
import TableFiles from './TableFiles';
import SearchFile from './SearchFile';

export default function Home() {

    console.log(sessionStorage);
    if (sessionStorage.getItem('server_port') == undefined) {
        console.log('working');
        return <JoinServer/>
      } 

    
    
      return ( 
          <div className="Home">
            <TableNodes/>
            <SearchFile/>

            <TableFiles/>
            </div>
        )
}