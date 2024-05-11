import React from "react";
import styles from "./index.module.css";
import Card from "../card";

const ProdDisplayHorizontal = ({products, title}) => {
    return (
        <div className={styles.display}>
            <h2>{title}</h2>
            <div className={styles.products}>
                {products.map(product => (
                    <Card key={product.id} product={product} small />
                ))}
            </div>
        </div>
    )
}

export default ProdDisplayHorizontal;