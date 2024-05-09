import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import Images from "../../components/images";

export const productLoader = async (product) => {
    let response = await fetch(`http://localhost:8080/rest/v1/get?prod=${product}`);
    let data = response.json();

    return data;
}

const Product = () => {
    const product = useLoaderData();

    return (
        <div className={styles.product}>
            <h2>{product.name}</h2>
            <Images images={product.images} />
        </div>
    )
}

export default Product;