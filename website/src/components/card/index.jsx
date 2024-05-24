import React from "react";
import styles from "./index.module.css";
import clsx from "clsx";
import { fixImgUrl } from "../../utils";

const Card = ({product, small = false}) => {
    let img = product?.images?.search?.resolutions[small ? "125X161" : "180X240"] ?? (small ? product?.image_125X161 : product?.image_180X240);
    return (
        <a 
            href={`/product/${product.id}`} 
            className={clsx(styles.card, small && styles.cardSmall)} >
            <div 
                className={clsx(small ? styles.imgContainerSmall : styles.imgContainer)} >
                <img 
                    className={clsx(small ? styles.prodImgSmall : styles.prodImg)} 
                    src={img ? fixImgUrl(img) : img} />
            </div>
            <strong 
                className={styles.brand}
                >
                {product.brandName}
            </strong>
            <div className={styles.name}>
                <span>{product?.name}</span>
            </div>
        </a>
    )
}

export default Card;