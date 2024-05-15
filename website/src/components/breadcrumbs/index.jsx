import React from "react";
import styles from "./index.module.css";
import { Chevron } from "../icons";

const Breadcrumbs = ({items}) => {
    return (
        <div className={styles.breadcrumbs}>
            {items.map((item, idx) => (
                <React.Fragment  key={idx}>
                {idx > 0 && <Chevron className={styles.chevron}/>}
                {idx + 1 === items.length ?
                <span className={styles.item}>{item}</span>
                :
                <a href={`/category/${idx === 0 ? "cat" : idx === 1 ? "sub" : "use"}/${item}`} className={styles.item}>{item}</a>}
                </React.Fragment>
            ))}
        </div>
    )
}

export default Breadcrumbs;