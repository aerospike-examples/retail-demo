import { useLoaderData } from "react-router-dom";
import styles from "./index.module.css";
import Card from "../../components/card";

const server = process.env.SERVER ?? import.meta.env.VITE_SERVER;

export const searchLoader = async ({ request }) => {
    let url = new URL(request.url);
    let query = url.searchParams.get("q");
    let response = await fetch(`${server}/rest/v1/search?q=${query}`);
    let results = await response.json();
    return { results, query };
}

export const categoryLoader = async (idx, filter) => {
    let index;
    switch (idx) {
        case "cat":
            index = "category";
            break;
        case "sub":
            index = "subCategory";
            break;
        case "use":
            index = "usage";
            break;
        default:
            index = ""
    }
    let response = await fetch(`${server}/rest/v1/category?idx=${index}&filter_value=${filter}`);
    
    let results = await response.json();
    return { results, filter };
}

const Products = () => {
    const {results: { products, time }, query = null, filter = null} = useLoaderData();

    return (
        <div className={styles.container}>
            <div className={styles.resultMeta}>
                {query && <span className={styles.filter}>Results for <strong>{query}</strong></span>}
                {filter && <span className={styles.filter}>Category <strong>{filter}</strong></span>}
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