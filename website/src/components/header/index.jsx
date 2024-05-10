import React, { useEffect, useState } from "react";
import styles from "./index.module.css";
import logo from "../../assets/logo.png";
import cart from "../../assets/shopping-cart.png";
import Profile from "../profile";

const Header = () => {
    const [query, setQuery] = useState("");

    useEffect(() => {
        let params = new URLSearchParams(window.location.search);
        let q = params.get("q");
        if(q) setQuery(q);
    }, [])

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
                            placeholder="Search"
                            value={query} 
                            onChange={(e) => setQuery(e.currentTarget.value)} />
                    </form>
                </nav>
                <div className={styles.controls}>
                    <Profile />
                    <img src={cart} className={styles.cart}/>
                </div>
            </div>
        </header>
    )
}

export default Header;