import { Outlet } from 'react-router-dom';
import styles from './index.module.css';

const App = () => {
  	return (
    	<div className={styles.app}>
			<Outlet />
    	</div>
  	)
}

export default App
