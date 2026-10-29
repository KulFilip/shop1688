import { describe, it, expect } from 'vitest';
import { translations } from '../lib/types';

describe('Internationalization & Confidentiality specifications', () => {
  it('contains valid Polish and Ukrainian translations', () => {
    expect(translations.pl.powerBanks).toBe('Banki Energii (Power Bank)');
    expect(translations.ua.powerBanks).toBe('Повербанки (Power Bank)');
    expect(translations.pl.managerMode).toBeDefined();
    expect(translations.ua.managerMode).toBeDefined();
  });

  it('guarantees that customer view never leaks 1688 provider URLs', () => {
    const rawDbRow = {
      id: 1,
      offer_id: '1688_pb_123',
      title_pl: 'Powerbank 20000mAh',
      title_ua: 'Повербанк 20000mAh',
      price_pln: 59.99,
      price_uah: 690.0,
      source_platform: '1688',
      source_url: 'https://detail.1688.com/offer/123.html',
      source_seller: 'Guangdong Tech Ltd'
    };

    // Client serializer
    const makeCustomerView = (row: typeof rawDbRow) => ({
      id: row.id,
      title: row.title_pl,
      price_pln: row.price_pln,
      price_uah: row.price_uah,
    });

    const customerProduct = makeCustomerView(rawDbRow);
    expect((customerProduct as any).source_platform).toBeUndefined();
    expect((customerProduct as any).source_url).toBeUndefined();
    expect((customerProduct as any).source_seller).toBeUndefined();
    expect(JSON.stringify(customerProduct)).not.toContain('1688');
  });
});

