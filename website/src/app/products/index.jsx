import { useLoaderData } from "react-router-dom";
import styles from "./index.module.css";
import Card from "../../components/card";

export const searchLoader = async ({ request }) => {
    let url = new URL(request.url);
    let query = url.searchParams.get("q");
    let response = await fetch(`http://localhost:8080/rest/v1/search?q=${query}`);
    let products = await response.json();
    
    return {products, query};
}

export const categoryLoader = async (category) => {
    let response = await fetch(`http://localhost:8080/rest/v1/category?cat=${category}`);
    let products = response.json();

    return {products, category};
}

const Products = () => {
    const {products, query = null, category = null} = useLoaderData();

    return (
        <div className={styles.container}>
            {query && <span className={styles.filter}>Results for <strong>{query}</strong></span>}
            {category && <span className={styles.filter}>Category <strong>{category}</strong></span>}
            <div className={styles.products}>
                {products.map(product => (
                    <Card key={product.id} product={product} />
                ))}
            </div>
        </div>
    )
}

export default Products;