/**
 * @jest-environment jsdom
 */

describe('Frontend Key Interactions', () => {
    
    beforeEach(() => {
        document.body.innerHTML = `
            <div class="detail-gallery">
                <img id="mainImage" src="main.jpg" />
                <div class="thumbnail-list">
                    <img class="thumb-img" src="thumb1.jpg" onclick="document.getElementById('mainImage').src=this.src" />
                    <img class="thumb-img" src="thumb2.jpg" onclick="document.getElementById('mainImage').src=this.src" />
                </div>
            </div>
            
            <a href="specs.pdf" id="pdfLink" target="_blank">Download PDF</a>
        `;
    });

    test('Thumbnail click should update main image src', () => {
        const mainImage = document.getElementById('mainImage');
        const thumbs = document.querySelectorAll('.thumb-img');
        
        expect(mainImage.src).toContain('main.jpg');
        
        // Simulate click on second thumbnail
        thumbs[1].click();
        expect(mainImage.src).toContain('thumb2.jpg');
        
        // Simulate click on first thumbnail
        thumbs[0].click();
        expect(mainImage.src).toContain('thumb1.jpg');
    });

    test('PDF download link should have correct target', () => {
        const pdfLink = document.getElementById('pdfLink');
        expect(pdfLink.getAttribute('target')).toBe('_blank');
        expect(pdfLink.getAttribute('href')).toMatch(/\.pdf$/);
    });
});