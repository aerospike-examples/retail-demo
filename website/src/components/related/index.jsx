import React from "react";
import styles from "./index.module.css";
import Card from "../card";

const Related = ({related}) => {
    return (
        <div className={styles.related}>
            <h2>Similar items</h2>
            <div className={styles.relatedItems}>
                {related.map(related => (
                    <Card key={related.id} product={related} small />
                ))}
            </div>
        </div>
    )
}

export default Related;