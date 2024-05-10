import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import Images from "../../components/images";
import Breadcrumbs from "../../components/breadcrumbs";
import ProductDetail from "../../components/productDetail";
import Related from "../../components/related";
import StyleOptions from "../../components/styleOptions";

export const productLoader = async (product) => {
    let response = await fetch(`http://localhost:8080/rest/v1/get?prod=${product}`);
    let data = response.json();

    return data;
}

const Product = () => {
    const { product, related } = useLoaderData();

    return (
        <>
            <Breadcrumbs items={[
                product?.category,
                product?.subCategory,
                product?.usage,
                product?.name
            ]} />
            <div className={styles.product}>
                <div className={styles.productData}>
                    <Images images={product.images} />
                    <ProductDetail name={product.name} descriptors={product?.descriptors} />
                </div>
                
                {product.styles && 
                <StyleOptions options={product.styles} />}

                <Related related={related} />
            </div>
        </>
    )
}

export default Product;