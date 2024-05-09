import React from "react";
import styles from "./index.module.css";

const Card = ({product}) => {
    return (
        <a href={`/product/${product.id}`} className={styles.card}>
            <img className={styles.prodImg} src={product?.images?.search?.resolutions["180X240"]} />
            <span><strong>{product.brandName}</strong></span>
            <span>{product?.name}</span>
        </a>
    )
}

export default Card;