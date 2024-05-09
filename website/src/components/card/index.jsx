import React from "react";
import styles from "./index.module.css";
import clsx from "clsx";

const Card = ({product, small = false}) => {
    let img = product?.images?.search?.resolutions[small ? "125X161" : "180X240"];
    img = img ? img.replace("http://", "https://") : img;
    return (
        <a 
            href={`/product/${product.id}`} 
            className={clsx(small ? styles.cardSmall : styles.card)} >
            <div 
                className={clsx(small ? styles.imgContainerSmall : styles.imgContainer)} >
                <img 
                    className={clsx(small ? styles.prodImgSmall : styles.prodImg)} 
                    src={img} />
            </div>
            <h3 
                className={styles.brand}
                >
                {product.brandName}
            </h3>
            <span>
                {product?.name}
            </span>
        </a>
    )
}

export default Card;