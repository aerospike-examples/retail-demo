import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import ProdDisplayHorizontal from "../../components/prodDisplayHorizontal";

const server = import.meta.env.VITE_SERVER;

export const homeLoader = async () => {
    let response = await fetch(`${server}/rest/v1/home`);
    let data = await response.json();
    return data;
}

const Home = () => {
    const categories = useLoaderData();
    return (
        <div className={styles.home}>
            {Object.keys(categories).map(key => (
                <ProdDisplayHorizontal key={key} products={categories[key]} title={key} />
            ))}
        </div>
    )
}

export default Home;