DROP DATABASE IF EXISTS hcmus_master_coffeehouse_sample;

CREATE DATABASE hcmus_master_coffeehouse_sample;

ALTER DATABASE hcmus_master_coffeehouse_sample CHARACTER SET = utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hcmus_master_coffeehouse_sample;

CREATE TABLE ProductType (
    ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    BriefName VARCHAR(256) NOT NULL UNIQUE,
    ExtraDescription VARCHAR(4096)
);

CREATE TABLE Product (
    ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    PName VARCHAR(512) NOT NULL UNIQUE,
    OnSale BOOLEAN,
    OnSaleFrom DATE,
    Price DECIMAL(9),
    PType INT,
    CONSTRAINT FK_ProductType FOREIGN KEY (PType) REFERENCES ProductType(ID) ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO
    ProductType(ID, BriefName, ExtraDescription)
VALUES
(1, 'Cà phê Việt Nam', 'Nhóm sản phẩm thuần Việt mang giá trị cốt lõi của công ty'),
(2, 'Cà phê máy', 'Cà phê mang hương vị quốc tế'),
(3, 'Cold brew', 'Thức uống mát lạnh cho ngày oi nóng'),
(4, 'Trà trái cây', 'Thức uống giải khát tốt cho sức khoẻ'),
(5, 'Trà sữa Macchiato', 'Sự hoà quyện tuyệt vời giữa trà sữa, kem và phô mai'),
(6, 'Cà phê đá xay', 'Sự kết hợp độc đáo giữa cà phê và đá xay'),
(7, 'Thức uống trái cây', 'Ngon, bổ, dưỡng, tất cả đều có'),
(8, 'Matcha - Chocolate', 'Dành cho khách hàng đam mê \'trà xanh\' hoặc sô-cô-la'),
(9, 'Bánh & Snack', 'Điểm tâm nhẹ nhàng cho ngày thêm năng lượng'),
(10, 'Cà phê gói', 'Phục vụ khách hàng mua sỉ'),
(11, 'Merchandise', 'Sản phẩm cho fan như bình giữ nhiệt, ly tách, túi xách,...');

INSERT INTO
    Product(PName, OnSale, OnSaleFrom, Price, PType)
VALUES
('Bạc sỉu', 1, '2014-01-01', 32000, 1),
('Cà phê đen', 1, '2014-01-01', 32000, 1),
('Cà phê sữa', 1, '2014-01-01', 32000, 1),
('Americano', 1, '2014-01-01', 40000, 2),
('Cappuccino', 1, '2014-01-01', 50000, 2),
('Caramel Macchiato', 1, '2014-01-01', 50000, 2),
('Espresso', 1, '2014-01-01', 40000, 2),
('Latte', 1, '2014-01-01', 50000, 2),
('Mocha', 1, '2014-01-01', 50000, 2),
('Cold brew truyền thống', 1, '2014-06-01', 45000, 3),
('Cold brew sữa tươi', 1, '2014-06-01', 45000, 3),
('Cold brew Phúc bồn tử', 0, '2014-06-01', 50000, 3),
('Trà trái vải', 0, '2015-02-04', 45000, 4),
('Trà hạt sen', 1, '2015-02-04', 45000, 4),
('Trà đào cam sả', 1, '2015-02-04', 45000, 4),
('Trà phúc bồn tử', 0, '2015-02-04', 50000, 4),
('Trà lài Macchiato', 1, '2015-02-04', 42000, 5),
('Trà Matcha Macchiato', 1, '2015-02-04', 45000, 5),
('Trà sữa Oolong nướng', 0, '2015-02-04', 50000, 5),
('Trà sữa mắc ca trân châu', 1, '2015-03-04', 50000, 5),
('Trà đen Macchiato', 1, '2015-05-01', 50000, 5),
('Hồng trà Latte Macchiato', 1, '2015-05-01', 55000, 5),
('Hồng trà sữa trân châu', 1, '2020-02-04', 55000, 5),
('Cà phê đá xay', 1, '2018-02-04', 59000, 6),
('Cookies đá xay', 1, '2019-02-04', 59000, 6),
('Chanh sả đá xay', 1, '2015-02-04', 49000, 7),
('Đào việt quất đá xay', 1, '2015-02-04', 59000, 7),
('Sinh tố việt quất', 1, '2015-02-04', 59000, 7),
('Sô cô la đá xay', 1, '2014-02-04', 59000, 8),
('Matcha đá xay', 1, '2014-02-04', 59000, 8),
('Matcha Latte', 1, '2014-02-04', 59000, 8),
('Bánh bao hai trứng cút', 1, '2016-02-04', 25000, 9),
('Bánh mì chà bông phô mai', 1, '2016-02-04', 32000, 9),
('Bánh mì que', 1, '2016-02-04', 12000, 9),
('Cơm cháy chà bông', 1, '2016-02-04', 35000, 9),
('Đậu phộng tỏi ớt', 1, '2016-02-04', 10000, 9),
('Mochi kem chocolate', 1, '2016-02-04', 19000, 9),
('Gà xé lá chanh', 1, '2016-02-04', 25000, 9),
('Cà phê gói', 1, '2014-02-04', 100000, 10),
('Cà phê phin', 1, '2014-02-04', 100000, 10),
('Bình giữ nhiệt Inox đen 500ml', 1, '2019-02-04', 300000, 11),
('Cốc sứ The Coffee House TPHCM', 1, '2019-02-04', 120000, 11),
('Túi Canvas Hà Nội', 0, '2019-02-04', 79000, 11);