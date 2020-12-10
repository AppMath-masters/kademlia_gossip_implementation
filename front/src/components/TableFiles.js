import React, {useState, useEffect} from 'react';
import axios from 'axios'
import AddFileModal from './AddFileModal';

function TableFiles() {

    const port = sessionStorage.getItem('server_port')
    const [data, setData] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);


    let fetchData = () => {

      setData(null);

        var query = 'http://localhost:'+port+'/content';
        axios
          .get((query), {
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded'
              }
          })
          .then(response => {
              setData(response.data);
              setIsLoaded(true);
            }
          )
          .catch(error => console.log(error));
      
    }

    useEffect(() => {
      
      fetchData();
    }, [isLoaded]);


    if(data != null) {

      if (data.length === 0){
        return( <div><AddFileModal/></div>);
      }

      console.log(data)

      return (
          <div><h1 align='center'>Files</h1> <AddFileModal/>
        <table className="table_info">
          <thead>
            <tr>
              <th>name</th>
              <th>path</th>
            </tr>
          </thead>
          <tbody>{data.map((info) => {return (<tr key={info.id}>
        <td>{info.name}</td>
        <td>{info.path}</td>
      </tr>);})}</tbody>
        </table>
        </div>
      );
    } else {
      //return( <Error flag={"wait"}/>);
      return( <div><AddFileModal/></div>);
    }

}

export default TableFiles;

