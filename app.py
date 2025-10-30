import streamlit as st
import openai
import json

# Set page config
st.set_page_config(page_title="BrandMatch AI", layout="wide")

# Securely set your API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# Sample influencer data
influencers = [
    {
        "name": "Isha Sharma",
        "handle": "@eco_with_isha",
        "followers": 18500,
        "engagement": 7.2,
        "niche": "Sustainable Fashion, Eco-Conscious Living",
        "location": "India",
        "recent_growth": 5.0,
        "content_style": "Reels, Long-form posts"
    },
    {
        "name": "Priya Jain",
        "handle": "@thegreeneditbypriya",
        "followers": 32200,
        "engagement": 5.8,
        "niche": "Indian Traditional Wear, Slow Fashion",
        "location": "India",
        "recent_growth": 2.0,
        "content_style": "IGTV, Reels, Stories"
    },
    {
        "name": "Saanvi Kapoor",
        "handle": "@saarisforchange",
        "followers": 11400,
        "engagement": 8.3,
        "niche": "Eco-Fashion, Saree Styling, Activism",
        "location": "India",
        "recent_growth": 10.0,
        "content_style": "Reels, Educational posts"
    },
    {
        "name": "Meera Nair",
        "handle": "@consciousstyle_meera",
        "followers": 25300,
        "engagement": 6.5,
        "niche": "Sustainable Fashion, Minimalism",
        "location": "India",
        "recent_growth": 8.0,
        "content_style": "Carousel posts, Reels"
    },
    {
        "name": "Ananya Singh",
        "handle": "@ananya.eco.diaries",
        "followers": 14800,
        "engagement": 7.8,
        "niche": "Women Empowerment, Eco-Products",
        "location": "India",
        "recent_growth": 12.0,
        "content_style": "Stories, Behind-the-scenes"
    },
]

# App title
st.title("🎯 BrandMatch AI")
st.markdown("### Micro-Influencer × Brand Collaboration CRM")
st.markdown("---")

# User type selection
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Who are you?")
user_type = st.radio("Select your role:", ["Brand", "Influencer"], horizontal=True)

st.markdown("---")

if user_type == "Brand":
    st.header("🏢 Brand Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input("Brand Name", value="GreenEarth Eco Fashion")
        brand_values = st.text_area("Brand Values (comma separated)", value="Sustainability, Women Empowerment, Ethical Manufacturing", height=80)
        product_type = st.text_input("Product Category", value="Eco-Friendly Sarees")
    
    with col2:
        target_audience = st.text_area("Target Audience Description", value="Women aged 20-35, eco-conscious, Tier 1/2 cities", height=80)
        campaign_budget = st.number_input("Campaign Budget per Influencer (₹)", value=25000, min_value=5000, max_value=100000)
    
    if st.button("🔍 Find Influencer Matches", use_container_width=True):
        st.markdown("---")
        
        # Scoring functions
        def get_authenticity_score(followers, engagement, recent_growth):
            """Calculate authenticity score (0-100)"""
            fake_spike = recent_growth > 30  # Suspicious if sudden spike
            engagement_score = min((engagement / 10) * 50, 50)
            growth_score = 35 if not fake_spike else 5
            base_score = 50 + engagement_score + growth_score
            return min(max(base_score, 0), 100)
        
        def get_fit_score(brand_vals, brand_aud, influencer_niche):
            """Calculate brand-influencer fit score (0-100)"""
            brand_vals_lower = [v.strip().lower() for v in brand_vals.split(",")]
            brand_aud_lower = [a.strip().lower() for a in brand_aud.split(",")]
            niche_lower = influencer_niche.lower()
            
            value_match = any(val in niche_lower for val in brand_vals_lower)
            audience_match = any(aud in niche_lower for aud in brand_aud_lower)
            
            score = 80 if value_match else 50
            score += 10 if audience_match else 0
            score += 10 if influencer_niche.lower().find("saree") >= 0 else 0
            return min(score, 100)
        
        # Calculate matches
        matches = []
        for inf in influencers:
            auth = get_authenticity_score(inf["followers"], inf["engagement"], inf["recent_growth"])
            fit = get_fit_score(brand_values, target_audience, inf["niche"])
            matches.append({
                "influencer": inf,
                "auth_score": int(auth),
                "fit_score": int(fit)
            })
        
        # Sort by fit score and authenticity
        matches.sort(key=lambda m: (m["fit_score"], m["auth_score"]), reverse=True)
        
        # Display results
        st.subheader("📊 Top Influencer Matches")
        
        for idx, m in enumerate(matches[:3], 1):
            inf = m["influencer"]
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {idx}. {inf['name']}")
                st.markdown(f"**Handle:** {inf['handle']}")
                st.markdown(f"**Niche:** {inf['niche']}")
                st.markdown(f"**Followers:** {inf['followers']:,} | **Engagement:** {inf['engagement']}%")
                st.markdown(f"**Location:** {inf['location']} | **Content Style:** {inf['content_style']}")
            
            with col2:
                st.metric("Authenticity", f"{m['auth_score']}/100")
            
            with col3:
                st.metric("Fit Score", f"{m['fit_score']}/100")
            
            # Collaboration idea
            st.markdown(f"**💡 Collaboration Idea:** Host an 'Eco-Saree Challenge' where {inf['name']} styles 3 sustainable saree looks, shares care tips, and encourages followers to share their own #EcoSaree stories.")
            
            # Generate AI outreach message
            if openai.api_key:
                try:
                    prompt = f"""Generate a professional, friendly 2-3 line outreach message from {brand_name} to {inf['name']} for a collaboration opportunity. The brand is about {brand_values}. Budget: ₹{campaign_budget}. Keep it concise and personalized."""
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=100
                    )
                    message = response.choices[0].message.content
                    st.markdown(f"**✉️ Example Outreach Message:**")
                    st.info(message)
                except Exception as e:
                    st.warning("⚠️ AI message generation unavailable (check API key)")
                    st.markdown(f"**✉️ Example Outreach Message:**")
                    st.info(f"Hi {inf['name'].split()[0]}, we love your {inf['niche']} content! We're launching a new eco-friendly saree collection and think your audience would be perfect. Interested in collaborating? Budget: ₹{campaign_budget}.")
            else:
                st.markdown(f"**✉️ Example Outreach Message:**")
                st.info(f"Hi {inf['name'].split()[0]}, we love your {inf['niche']} content! We're launching a new eco-friendly saree collection and think your audience would be perfect. Interested in collaborating? Budget: ₹{campaign_budget}.")
            
            st.markdown("---")

elif user_type == "Influencer":
    st.header("👤 Influencer Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        inf_name = st.text_input("Your Name", value="Riya Eco")
        inf_niche = st.text_area("Your Niche (comma separated)", value="Eco-Fashion, Sustainable Living", height=80)
        follower_count = st.number_input("Followers", value=15000, min_value=1000, max_value=1000000)
    
    with col2:
        engagement_rate = st.number_input("Engagement Rate (%)", value=7.5, min_value=0.0, max_value=100.0)
        location = st.text_input("Location", value="India")
        recent_growth = st.number_input("Recent 30-day follower growth (%)", value=8.0, min_value=0.0)
    
    if st.button("🔍 Find Brand Partnerships", use_container_width=True):
        st.markdown("---")
        
        # Mock brands
        brands = [
            {"name": "SundarEarth", "values": "Sustainability, Eco-Friendly", "audience": "Women 20-35", "product": "Organic Sarees", "budget": 25000},
            {"name": "PureWeave Naturals", "values": "Slow Fashion, Women Empowerment", "audience": "Millennials", "product": "Handloom Cotton", "budget": 20000},
            {"name": "VastraVeda", "values": "Natural Fabrics, Fair Trade", "audience": "Corporate Women", "product": "Office Wear", "budget": 30000},
            {"name": "EcoThreads", "values": "Sustainability, Minimalism", "audience": "Young Professionals", "product": "Casual Wear", "budget": 22000},
        ]
        
        def get_authenticity_score(followers, engagement, recent_growth):
            fake_spike = recent_growth > 30
            engagement_score = min((engagement / 10) * 50, 50)
            growth_score = 35 if not fake_spike else 5
            base_score = 50 + engagement_score + growth_score
            return min(max(base_score, 0), 100)
        
        def get_brand_fit_score(brand, niche):
            niche_lower = niche.lower()
            value_match = any(val.strip().lower() in niche_lower for val in brand["values"].split(","))
            audience_match = any(aud.strip().lower() in niche_lower for aud in brand["audience"].split(","))
            score = 80 if value_match else 50
            score += 10 if audience_match else 0
            return min(score, 100)
        
        auth = get_authenticity_score(follower_count, engagement_rate, recent_growth)
        matches = []
        for br in brands:
            fit = get_brand_fit_score(br, inf_niche)
            matches.append({"brand": br, "fit_score": int(fit)})
        
        matches.sort(key=lambda x: x["fit_score"], reverse=True)
        
        st.subheader("🏆 Top Brand Partnership Opportunities")
        
        for idx, m in enumerate(matches[:3], 1):
            br = m["brand"]
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {idx}. {br['name']}")
                st.markdown(f"**Values:** {br['values']}")
                st.markdown(f"**Target Audience:** {br['audience']}")
                st.markdown(f"**Product:** {br['product']}")
                st.markdown(f"**Budget per Campaign:** ₹{br['budget']:,}")
            
            with col2:
                st.metric("Fit Score", f"{m['fit_score']}/100")
            
            st.markdown(f"**💡 Content Idea:** Create a 'Day in My Life' styling video wearing only {br['name']} products, showcasing sustainability in everyday fashion.")
            
            if openai.api_key:
                try:
                    prompt = f"""Write a short 2-3 line pitch from influencer {inf_name} to brand {br['name']} for a collaboration. The influencer focuses on {inf_niche}."""
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=100
                    )
                    pitch = response.choices[0].message.content
                    st.markdown(f"**💌 Example Pitch to Brand:**")
                    st.info(pitch)
                except:
                    st.info(f"Hi {br['name']} team! I create content around {inf_niche} and my audience (followers: {follower_count:,}) matches your target market. Let's collaborate!")
            else:
                st.info(f"Hi {br['name']} team! I create content around {inf_niche} and my audience (followers: {follower_count:,}) matches your target market. Let's collaborate!")
            
            st.markdown("---")

# Footer
st.markdown("---")
st.markdown("**Built with ❤️ using Streamlit | BrandMatch AI - Micro-Influencer × Brand CRM**")
