import React, { useState } from 'react';
import './styles.css';

const Nyxiee = () => {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  const toggleChatbot = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">NYKAA</div>
        <ul className="nav-links">
          <li>Categories</li>
          <li>Brands</li>
          <li>Luxe</li>
          <li>Nykaa Fashion</li>
          <li>Beauty Advice</li>
        </ul>
        <div className="nav-right">
          <input type="text" placeholder="Search on Nykaa" className="search-bar" />
          <button className="sign-in-btn">Sign in</button>
        </div>
      </nav>

      {/* Deals Section */}
      <div className="deals-section">
        <h2 className="deals-heading">
          DEALS <span>AS VIBRANT AS YOU</span>
        </h2>
        <div className="deals-container">
          {/* Deal Box */}
          <DealBox
            imgSrc="img8.jpg"
            brand="FENTY BEAUTY"
            description="Global Bestsellers"
            link="#"
          />
          <DealBox
            imgSrc="img3.jpg"
            brand="MAYBELLINE"
            description="Up To 35% Off On Bestsellers"
          />
          <DealBox
            imgSrc="img18.webp"
            brand="NARS Radiant"
            description="Up To 27% Off On Makeup Bestsellers"
          />
          <DealBox
            imgSrc="img4.jpg"
            brand="NYKAA COSMETICS"
            description="Up To 35% Off On Makeup Bestsellers"
          />
          <DealBox
            imgSrc="img11.jpg"
            brand="SunSilk"
            description="Up To 12% Off On Makeup Bestsellers"
          />
          <DealBox
            imgSrc="img12.avif"
            brand="NIVEA Skincare"
            description="Up To 49% Off On Makeup"
          />
          <DealBox
            imgSrc="img13.webp"
            brand="Himayala Herbals"
            description="Up To 50% Off On Makeup Bestsellers"
          />
          <DealBox
            imgSrc="img2.png"
            brand="Kay Beauty"
            description="Up To 20% Off On Bestsellers"
          />
          <DealBox
            imgSrc="img16.jpg"
            brand="MAC Comestics"
            description="Up To 17% Off for Bestsellers"
          />
          <DealBox
            imgSrc="img5.jpg"
            brand="L'OREAL"
            description="Up To 35% Off On Bestsellers"
          />
        </div>
      </div>

      {/* Chatbot Button (Circle) */}
      <div className="chatbot-button" onClick={toggleChatbot}>
        <span>Nyxiee</span>
      </div>

      {/* Chatbot Iframe */}
      {isChatbotOpen && (
        <div className="chatbot-container">
          <iframe
    allow="microphone;"
    width="350"
    height="430"
    src="https://console.dialogflow.com/api-client/demo/embedded/82b182cd-2491-443c-8ec8-6a5818657521">
</iframe>
        </div>
      )}
    </div>
  );
};

// DealBox component
const DealBox = ({ imgSrc, brand, description, link }) => {
  return (
    <div className="deal-box">
      <img src={imgSrc} alt={brand} />
      <p className="brand">{brand}</p>
      <p>{description}</p>
      {link && <a href={link}>Shop Now</a>}
    </div>
  );
};

export default Nyxiee;
