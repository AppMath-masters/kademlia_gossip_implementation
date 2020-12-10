import logo from './logo.svg';
import './App.css';
import './Home.css';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './components/Home';

function App() {
  return (
		<div>
			<Home/>
		</div>
	);
}

export default App;
