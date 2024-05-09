import { Outlet } from 'react-router-dom';
import styles from './index.module.css';
import Header from '../components/header';
import Footer from '../components/footer';

const App = () => {
  	return (
    	<div className={styles.app}>
			<Header />
			<div className={styles.container}>
				<Outlet />
			</div>
			<Footer />
    	</div>
  	)
}

export default App
