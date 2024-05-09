import React from "react";
import styles from "./index.module.css";
import logo from "../../assets/logo.png";

const Header = () => {
    return (
        <header className={styles.header}>
            <div className={styles.headContainer}>
                <a href="/"><img src={logo} alt="Logo" className={styles.logo} /></a>
                <nav className={styles.nav}>
                    <form method="get" action="/search">
                        <input 
                            className={styles.search} 
                            type='search' 
                            name="q" 
                            placeholder="Search" />
                    </form>
                </nav>
            </div>
        </header>
    )
}

export default Header;