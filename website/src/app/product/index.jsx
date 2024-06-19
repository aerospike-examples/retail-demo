import React from "react";
import styles from "./index.module.css";
import { useLoaderData } from "react-router-dom";
import Images from "../../components/images";
import Breadcrumbs from "../../components/breadcrumbs";
import ProductDetail from "../../components/productDetail";
import StyleOptions from "../../components/styleOptions";
import ProdDisplayHorizontal from "../../components/prodDisplayHorizontal";
import SizeOptions from "../../components/sizeOptions";

const server = process.env.SERVER ?? import.meta.env.VITE_SERVER;

export const productLoader = async (product) => {
    let response = await fetch(`${server}/rest/v1/get?prod=${product}`);
    let { error, ...data } = await response.json();

    if(error) throw new Response("", {
        status: 404,
        statusText: "Not Found"
    });
    return data;
}

const Product = () => {
    const { product, related, also_bought } = useLoaderData();

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
                    <div className={styles.options}>
                        <Images images={product.images} />
                        {product.styles && 
                        <StyleOptions options={product.styles} />}
                    </div>
                    <div className={styles.options}>
                        <ProductDetail name={product.name} descriptors={product?.descriptors} />
                        {product.options.length > 1 &&
                        <SizeOptions options={product.options} />}
                    </div>
                </div>
                <ProdDisplayHorizontal products={related} title="Similar items" />
                <ProdDisplayHorizontal products={also_bought} title="Also bought" />
            </div>
        </>
    )
}

export default Product;