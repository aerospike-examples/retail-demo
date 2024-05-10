import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import Card from "../../components/card";

export const homeLoader = async () => {
    let response = await fetch(`http://localhost:8080/rest/v1/home`);
    let data = response.json();
    
    return data;
}

const Home = () => {
    const data = useLoaderData();
    console.log(data)
    return (
        <div className={styles.home}>
            <h2>Accessories</h2>
            <div className={styles.accessories}>
                {data.map(product => (
                    <Card key={product.id} product={product} />
                ))}
            </div>
        </div>
    )
}

export default Home;