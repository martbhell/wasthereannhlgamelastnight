/* https://github.com/rikschennink/shiny */
shiny('.shiny', {
    // type of shiny to render,
    // 'background', 'border', or 'text'
    type: 'background',
    gradient: {

        // type of gradient
        // 'linear' or 'radial'
        type: 'linear',

        // angle of gradient when type is linear
        angle: '120deg',

        // flip axis movement
        flip: {
            x: true,
            y: false
        },

        // colors to use
        colors: [
            // offset, color, opacity
            // ! don't pass rgba or hsla colors, supply the opacity seperately
            [.1, '#eee'],
            [.25, '#888'],
            [.35, '#999'],
            [.35, '#fff'],
            [.35, '#fff'],
            [.75, '#999'],
            [.75, '#fff']
        ]

    },

    // optional pattern fill
    pattern: {
        type: 'noise', // only 'noise' for now
        opacity: .5
    }
});
