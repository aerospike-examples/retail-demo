import React from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home, { homeLoader } from './app/home';
import Product, { productLoader } from './app/product';
import Products, { searchLoader, categoryLoader } from './app/products';
import App from './app';
import NotFound from './app/notFound';

const Routes = () => {
    const router = createBrowserRouter([
        {
            path: '/', 
            element: <App />,
            errorElement: <NotFound />,
            children: [{
                errorElement: <NotFound />,
                children: [
                    {index: true, element: <Home />, loader: homeLoader},
                    {path: "/search", element: <Products />, loader: searchLoader},
                    {path: "/product/:product", element: <Product />, loader: ({params: { product }}) => productLoader(product)},
                    {path: "/category/:idx/:filter", element: <Products />, loader: ({params: { idx, filter }}) => categoryLoader(idx, filter)}
                ]
            }]
        }
    ]);

    return <RouterProvider router={router} />
}

export default Routes;