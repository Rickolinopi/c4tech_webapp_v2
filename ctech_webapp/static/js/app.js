function toggleMenu() {
    const menu = document.getElementById("menu");

    if (menu) {
        menu.classList.toggle("open");
    }
}


function filterProducts() {

    const input = document.getElementById("search");

    if (!input) {
        return;
    }

    const value = input.value.toLowerCase();

    const products = document.querySelectorAll(".product-card");

    products.forEach(function(product) {

        const name = product.dataset.name || "";

        if (name.includes(value)) {
            product.style.display = "";
        } else {
            product.style.display = "none";
        }

    });
}


async function setStatus(orderId, status) {

    try {

        const response = await fetch(
            `/api/pedido/${orderId}/status`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: status
                })
            }
        );

        if (response.ok) {
            window.location.reload();
        }

    } catch (error) {
        console.error(error);
    }
}