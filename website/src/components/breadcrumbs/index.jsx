import React from "react";
import styles from "./index.module.css";
import { Chevron } from "../icons";

const Breadcrumbs = ({items}) => {
    return (
        <div className={styles.breadcrumbs}>
            {items.map((item, idx) => (
                <React.Fragment  key={idx}>
                {idx > 0 && <Chevron className={styles.chevron}/>}
                <span className={styles.item}>{item}</span>
                </React.Fragment>
            ))}
        </div>
    )
}

export default Breadcrumbs;