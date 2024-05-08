import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";

const Product = () => {
    const product = useLoaderData();

    return (
        <div className={styles.product}>
            <span>{product.name}</span>
        </div>
    )
}

export default Product;