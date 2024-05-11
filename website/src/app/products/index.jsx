import { useLoaderData } from "react-router-dom";
import styles from "./index.module.css";
import Card from "../../components/card";

export const searchLoader = async ({ request }) => {
    let url = new URL(request.url);
    let query = url.searchParams.get("q");
    let response = await fetch(`http://localhost:8080/rest/v1/search?q=${query}`);
    let results = await response.json();
    return {results, query};
}

export const categoryLoader = async (category) => {
    let response = await fetch(`http://localhost:8080/rest/v1/category?cat=${category}`);
    let results = await response.json();
    return {results, category};
}

const Products = () => {
    const {results: { products, time }, query = null, category = null} = useLoaderData();

    return (
        <div className={styles.container}>
            <div className={styles.resultMeta}>
                {query && <span className={styles.filter}>Results for <strong>{query}</strong></span>}
                {category && <span className={styles.filter}>Category <strong>{category}</strong></span>}
                <span className={styles.time}>Query executed in {time}ms</span>
            </div>
            <div className={styles.products}>
                {products.map(product => (
                    <Card key={product.id} product={product} />
                ))}
            </div>
        </div>
    )
}

export default Products;