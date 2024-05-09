import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";

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
        </div>
    )
}

export default Home;