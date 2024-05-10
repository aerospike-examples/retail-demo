import React, { useEffect, useRef, useState } from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import Images from "../../components/images";
import Card from "../../components/card";
import Breadcrumbs from "../../components/breadcrumbs";
import clsx from "clsx";
import { Chevron } from "../../components/icons";

export const productLoader = async (product) => {
    let response = await fetch(`http://localhost:8080/rest/v1/get?prod=${product}`);
    let data = response.json();

    return data;
}

const Product = () => {
    const { product, related } = useLoaderData();
    const [open, setOpen] = useState(false);
    const [height, setHeight] = useState(350);
    const [elemHeight, setElemHeight] = useState(0);

    const toggleOpen = () => {
        setOpen(!open);
        setHeight(open ? 350 : elemHeight + 32);
    }

    const descriptionRef = useRef(null);
    useEffect(() => {
        console.log(product);
        setElemHeight(descriptionRef?.current?.clientHeight)
    }, [])

    return (
        <div className={styles.product}>
            <Breadcrumbs items={[
                product?.category,
                product?.subCategory,
                product?.usage
            ]} />
            <div className={styles.productData}>
                <Images images={product.images} />
                <div className={styles.prodDetail}>
                    <h2>{product.name}</h2>
                    <div className={styles.descContainer} style={{height: `${height}px`}}>
                        <div 
                            className={styles.description} 
                            dangerouslySetInnerHTML={{__html: product?.descriptors?.description?.value}}
                            ref={descriptionRef} />
                    </div>
                    {elemHeight > 350 &&
                    <div className={styles.more} onClick={toggleOpen}>
                        <Chevron className={clsx(styles.chevron, open && styles.open)} />
                    </div>}
                </div>
            </div>
            <h2>Other items you may like</h2>
            <div className={styles.related}>
                {related.map(related => (
                    <Card key={related.id} product={related} small />
                ))}
            </div>
        </div>
    )
}

export default Product;