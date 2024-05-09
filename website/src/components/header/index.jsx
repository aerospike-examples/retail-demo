import React from "react";
import styles from "./index.module.css";

const Header = () => {
    return (
        <header>
            <nav className={styles.nav}>
                <form method="get" action="/search">
                    <input 
                        className={styles.search} 
                        type='search' 
                        name="q" 
                        placeholder="Search" />
                </form>
            </nav>
        </header>
    )
}

export default Header;