import { NextRequest, NextResponse } from 'next/server';
import { getDbPool } from '@/lib/db';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const lang = searchParams.get('lang') === 'ua' ? 'ua' : 'pl';
    const isManager = searchParams.get('manager') === 'true';
    const query = searchParams.get('q') || '';
    const category = searchParams.get('category') || 'power bank';
    const limit = Math.min(parseInt(searchParams.get('limit') || '50', 10), 100);

    const pool = getDbPool();

    let sql = `
      SELECT 
        id, offer_id, category,
        title_pl, title_ua,
        description_pl, description_ua,
        weight, dimensions, main_image, images,
        price_cny, margin, price_pln, price_uah,
        min_order_quantity, in_stock,
        source_platform, source_url, source_seller, raw_attributes, updated_at
      FROM products
      WHERE 1=1
    `;
    const params: (string | number)[] = [];

    if (category) {
      params.push(category);
      sql += ` AND category = $${params.length}`;
    }

    if (query) {
      params.push(`%${query}%`);
      sql += ` AND (title_pl ILIKE $${params.length} OR title_ua ILIKE $${params.length} OR description_pl ILIKE $${params.length})`;
    }

    sql += ` ORDER BY id ASC LIMIT $${params.length + 1}`;
    params.push(limit);

    const { rows } = await pool.query(sql, params);

    // Format output: hide sensitive 1688 provider fields unless manager auth/parameter is verified
    const products = rows.map((row) => {
      const isUa = lang === 'ua';
      const baseProduct = {
        id: row.id,
        offer_id: row.offer_id,
        category: row.category,
        title: isUa ? row.title_ua : row.title_pl,
        description: isUa ? row.description_ua : row.description_pl,
        weight: row.weight,
        dimensions: row.dimensions,
        main_image: row.main_image,
        images: row.images,
        price_pln: Number(row.price_pln),
        price_uah: Number(row.price_uah),
        in_stock: row.in_stock,
      };

      if (isManager) {
        return {
          ...baseProduct,
          price_cny: Number(row.price_cny),
          margin: Number(row.margin),
          source_platform: row.source_platform,
          source_url: row.source_url,
          source_seller: row.source_seller,
          raw_attributes: row.raw_attributes,
          updated_at: row.updated_at,
        };
      }

      // Customer view: completely scrubbed of supplier origins
      return baseProduct;
    });

    return NextResponse.json({
      success: true,
      total: products.length,
      category,
      products,
    });
  } catch (error) {
    console.error('API products error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch products' },
      { status: 500 }
    );
  }
}

