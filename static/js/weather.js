(function() {
    'use strict'

    const cityInput = document.querySelector('input[name="city"]')
    const suggestions = []

    const popularCities = [
        'New York', 'London', 'Tokyo', 'Beijing', 'Paris', 'Berlin',
        'Sydney', 'Mumbai', 'Sao Paulo', 'Moscow', 'Toronto', 'Delhi',
        'Shanghai', 'Mexico City', 'Cape Town', 'Rio de Janeiro', 'Seoul',
        'Amsterdam', 'Madrid', 'Rome', 'Los Angeles', 'Chicago', 'Houston',
        'San Francisco', 'Boston', 'Seattle', 'Miami', 'Dallas', 'Denver'
    ]

    if (cityInput) {
        let dropdownCreated = false
        let dropdown = null

        cityInput.addEventListener('input', function() {
            const input = this.value.toLowerCase()
            if (input.length === 0) {
                if (dropdown) {
                    dropdown.innerHTML = ''
                    dropdown.classList.add('d-none')
                }
                return
            }

            if (!dropdownCreated) {
                dropdown = document.createElement('ul')
                dropdown.className = 'dropdown-menu show w-100'
                dropdown.style.position = 'absolute'
                dropdown.style.zIndex = '1050'
                cityInput.parentNode.appendChild(dropdown)
                dropdownCreated = true
            }

            const matches = popularCities.filter(c => c.toLowerCase().includes(input))
            dropdown.innerHTML = ''

            matches.slice(0, 8).forEach(city => {
                const item = document.createElement('li')
                const link = document.createElement('a')
                link.className = 'dropdown-item'
                link.href = `/weather/?city=${encodeURIComponent(city)}`
                link.textContent = city
                item.appendChild(link)
                dropdown.appendChild(item)
            })

            if (matches.length === 0) {
                const item = document.createElement('li')
                const link = document.createElement('a')
                link.className = 'dropdown-item'
                link.href = `/weather/?city=${encodeURIComponent(this.value)}`
                link.textContent = this.value
                item.appendChild(link)
                dropdown.appendChild(item)
            }

            dropdown.classList.remove('d-none')
        })

        document.addEventListener('click', function(e) {
            if (dropdown && dropdownCreated && !cityInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('d-none')
            }
        })
    }
})()
