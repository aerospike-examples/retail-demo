import React, { useState } from "react";
import styles from "./index.module.css";

const Home = () => {
    const [query, setQuery] = useState('');
	const [products, setProducts] = useState([]);

	const handleSearch = async (e) => {
		e.preventDefault();
		let response = await fetch(`http://localhost:8080/rest/v1/search?q=${query}`);
		let data = await response.json();
		setProducts(data);
	}

    return (
        <div className={styles.home}>
            <form onSubmit={handleSearch}>
				<input
					className={styles.search} 
					type='search' 
					value={query} 
					onChange={(e) => setQuery(e.currentTarget.value)} />
			</form>
            <div className={styles.prodContainer}>
				{products.map(product => (
					<div key={product.id}>
						<a href={`/product/${product.id}`}>
							<img className={styles.prodImg} src={product?.images?.search?.resolutions["150X200"]} />
						</a>
						<span>{product.distance}</span>
					</div>
				))}
			</div>
        </div>
    )
}

export default Home;