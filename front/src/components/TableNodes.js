import React, {useState, useEffect} from 'react';
import axios from 'axios'

function TableNodes() {

    const port = sessionStorage.getItem('server_port')
    const [data, setData] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);


    let fetchData = () => {

      setData(null);

        var query = 'http://localhost:'+port+'/neighbors';
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
        return( <div>Error</div>);
      }

      console.log(data)

      return (
          <div><h1 align='center'>Neighbors</h1>
        <table className="table_info">
          <thead>
            <tr>
              <th>id</th>
              <th>ip</th>
              <th>port</th>
            </tr>
          </thead>
          <tbody>{data.map((info) => {return (<tr key={info.id}>
        <td>{info.id}</td>
        <td>{info.ip}</td>
        <td>{info.port}</td>
      </tr>);})}</tbody>
        </table>
        </div>
      );
    } else {
      //return( <Error flag={"wait"}/>);
      return( <div> Error</div>);
    }

}

export default TableNodes;

