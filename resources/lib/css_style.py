STYLE = """
body {
    background: linear-gradient(to left, #648880, #293f50);
    font-family:Courier New,Courier,monospace;
    font-size:30px;
    text-align: center;
}

table {
    border-collapse:collapse; 
    text-align:center;
    margin: 0 auto;
}

th {
    border-bottom:2px solid grey; 
    color: white;
}

.container {
    position: relative;
    transition: transform .5s;
    width: 300px;
}

.image {
    display: block;
    width: 300px;
    height: 450px;
}

.container:hover {
    transform: scale(1.2);
    z-index: 1;
}

.container:hover .overlay {
    opacity: 0.8;
}

.overlay {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    width: 301px;
    height: 451px;
    opacity: 0;
    transition: .5s ease;
    background-color: #293f50 ;
}

.text {
    color: white;
    font-size: 20px;
    position: absolute;
    top: 50%;
    left: 50%;
    -webkit-transform: translate(-50%, -50%);
    -ms-transform: translate(-50%, -50%);
    transform: translate(-50%, -50%);
    text-align: center;
    border-collapse:collapse;
}"""
